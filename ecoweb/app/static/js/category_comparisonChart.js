async function drawCompanyComparisonChart(institutionType = "공공기관") {
    try {
        // 데이터 가져오기
        const response = await fetch('/static/js/institution_data.json');
        const data = await response.json();
        console.log("institution_data: ", data);
        
        // 현재 기관 타입의 데이터 찾기
        const institutionData = data.institutions.find(inst => inst.type === institutionType);
        if (!institutionData) {
            // 없으면 공공기관 데이터 사용하세요
            institutionData = data.institutions.find(inst => inst.type === "공공기관");
        }
        // 

        // 데이터 정렬 (오름차순)
        const sortedSizes = institutionData.data
            .map(item => item.size_mb)
            .sort((a, b) => a - b);

        // 현재 세션의 mbWeight 가져오기
        const mbWeight = window.mbWeight || 0;

        // 백분위 계산
        const percentile = calculatePercentile(sortedSizes, mbWeight);
        
        // 차트 데이터 준비
        const ctx = document.getElementById('companyComparisonChart').getContext('2d');
        
        // 분포 데이터 생성 (100개 구간으로 나누기)
        const binCount = 100;
        const binSize = (Math.max(...sortedSizes) - Math.min(...sortedSizes)) / binCount;
        const bins = Array.from({length: binCount}, (_, i) => {
            const start = Math.min(...sortedSizes) + (i * binSize);
            return sortedSizes.filter(size => size >= start && size < start + binSize).length;
        });

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Array.from({length: binCount}, (_, i) => 
                    ((Math.min(...sortedSizes) + (i * binSize)).toFixed(2))),
                datasets: [{
                    label: '기관 수',
                    data: bins,
                    backgroundColor: '#198754',
                    borderColor: '#198754',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    annotation: {
                        annotations: {
                            line1: {
                                type: 'line',
                                xMin: mbWeight,
                                xMax: mbWeight,
                                borderColor: 'red',
                                borderWidth: 2,
                                label: {
                                    content: `현재 웹사이트 (상위 ${(100-percentile).toFixed(1)}%)`,
                                    enabled: true,
                                    position: 'top'
                                }
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.parsed.y}개 기관`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: '배출량 (MB)'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: '기관 수'
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating comparison chart:', error);
    }
}

// 백분위 계산 함수
function calculatePercentile(sortedArray, value) {
    const index = sortedArray.findIndex(x => x >= value);
    if (index === -1) return 0;
    return (index / sortedArray.length) * 100;
}

// 페이지 로드 시 차트 생성
document.addEventListener('DOMContentLoaded', () => {
    // 세션에서 institution_type 가져오기
    const institutionType = "{{ session.get('institution_type', '공공기관')}}";  // Ensure it's properly formatted
    drawCompanyComparisonChart(institutionType);
});