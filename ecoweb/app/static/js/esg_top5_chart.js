async function createEsgTop5Chart() {
    try {
        const response = await fetch('/static/statistics/top5_efficient_sites.json');
        const data = await response.json();
        
        // 데이터 준비
        const labels = data.map(item => item.siteName);
        const values = data.map(item => item.transferSize);
        const categories = data.map(item => item.institutionCategory);
        
        const ctx = document.getElementById('esgTop5Chart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: '웹사이트 크기 (KB)',
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
                                const index = context.dataIndex;
                                return `${categories[index]}: ${context.raw.toFixed(2)}KB`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: '웹사이트 크기 (KB)'
                        },
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        ticks: {
                            callback: function(value, index) {
                                // 긴 사이트 이름을 줄여서 표시
                                const label = labels[index];
                                return label.length > 20 ? label.substr(0, 20) + '...' : label;
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating ESG Top 5 chart:', error);
    }
}

// 페이지 로드 시 차트 생성
document.addEventListener('DOMContentLoaded', createEsgTop5Chart);