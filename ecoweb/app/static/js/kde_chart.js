async function createKDEChart(currentMB) {
    try {
        // 공공기관 데이터와 HTTP Archive 데이터 로드
        const [publicResponse, httpArchiveResponse] = await Promise.all([
            fetch('/static/statistics/distribution_data.json'),
            fetch('/static/statistics/http_archive_data.json')
        ]);
        
        const publicData = await publicResponse.json();
        const httpArchiveData = await httpArchiveResponse.json();

        // HTTP Archive 데이터에서 desktop mbytes 추출
        const worldData = httpArchiveData
            .filter(d => d.client === 'desktop')
            .map(d => parseFloat(d.mbytes));

        // KDE 계산 함수
        function kernelDensityEstimator(kernel, X) {
            return function(V) {
                return X.map(x => [x, d3.mean(V, v => kernel(x - v))]);
            };
        }

        function kernelEpanechnikov(bandwidth) {
            return x => Math.abs(x /= bandwidth) <= 1 ? 0.75 * (1 - x * x) / bandwidth : 0;
        }

        // x축 범위 생성 (0MB ~ 10MB)
        const xValues = Array.from({length: 1000}, (_, i) => i * 0.01);
        
        // 세계 평균 KDE 계산
        const kde = kernelDensityEstimator(kernelEpanechnikov(1.5), xValues);
        const worldDensity = kde(worldData);

        // 한국 평균 정규분포 계산 (평균 4.7MB, 표준편차 1.5)
        function gaussianKDE(x, mean, std) {
            return Math.exp(-0.5 * Math.pow((x - mean) / std, 2)) / (std * Math.sqrt(2 * Math.PI));
        }
        const koreaY = xValues.map(x => gaussianKDE(x, 4.7, 1.5));

        const ctx = document.getElementById('kdeChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [
                    {
                        label: '공공기관 분포',
                        data: publicData.kde_points,
                        borderColor: 'rgba(13, 110, 253, 0.8)',
                        backgroundColor: 'rgba(13, 110, 253, 0.1)',
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: '세계 평균 분포',
                        data: worldDensity.map(d => ({x: d[0], y: d[1]})),
                        borderColor: 'rgba(90, 100, 95, 0.6)',
                        backgroundColor: 'rgba(90, 100, 95, 0.1)',
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: '한국 평균 분포',
                        data: xValues.map((x, i) => ({
                            x: x,
                            y: koreaY[i]
                        })),
                        borderColor: 'rgba(25, 135, 84, 0.9)',
                        backgroundColor: 'rgba(25, 135, 84, 0.15)',
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: '현재 웹사이트',
                        data: currentMB,
                        borderColor: 'rgba(255, 99, 132, 0.9)',
                        backgroundColor: 'rgba(255, 99, 132, 0.15)',
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    annotation: {
                        common: {
                            drawTime: 'afterDraw'
                        },
                        annotations: {
                            currentLine: {
                                type: 'line',
                                scaleID: 'x',  // x축에 연결
                                value: currentMB,  // xMin, xMax 대신 value 사용
                                borderColor: 'rgb(255, 99, 132)',
                                borderWidth: 2,
                                label: {
                                    font: {
                                        size: 9
                                    },
                                    display: true,
                                    position: 'top'
                                }
                            }
                        }
                    },
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    x: {
                        type: 'linear',  // 선형 스케일 사용
                        title: {
                            display: true,
                            text: '탄소배출량 (g CO₂)'
                        },
                        min: 0,
                        max: 15  // 최대 범위 조정
                    },
                    y: {
                        title: {
                            display: true,
                            text: '밀도'
                        },
                        min: 0
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating KDE chart:', error);
    }
}