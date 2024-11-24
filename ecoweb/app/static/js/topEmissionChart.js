async function createTopEmissionChart() {
    try {
        const response = await fetch('/static/statistics/top5_bad_sites.json');
        const data = await response.json();
        
        // 데이터 정렬 (큰 순서대로)
        data.sort((a, b) => b.transferSize - a.transferSize);
        
        // 차트 데이터 준비
        const labels = data.map(item => {
            // 긴 사이트명 줄이기
            return item.siteName.length > 15 
                ? item.siteName.substring(0, 15) + '...' 
                : item.siteName;
        });
        
        const values = data.map(item => (item.transferSize / 1024).toFixed(2)); // MB로 변환
        
        // 차트 생성
        const ctx = document.getElementById('topEmissionChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: '배출량',
                    data: values,
                    backgroundColor: '#198754',
                    borderColor: '#198754',
                    borderWidth: 1
                }]
            },
            options: {
                indexAxis: 'y',  // 수평 막대 그래프
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const item = data[context.dataIndex];
                                return `${item.siteName} (${item.institutionCategory}): ${context.formattedValue}MB`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        grid: {
                            display: false
                        },
                        ticks: {
                            callback: function(value) {
                                return value + 'MB';
                            }
                        }
                    },
                    y: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating top emission chart:', error);
    }
}

// 페이지 로드 시 차트 생성
document.addEventListener('DOMContentLoaded', createTopEmissionChart);