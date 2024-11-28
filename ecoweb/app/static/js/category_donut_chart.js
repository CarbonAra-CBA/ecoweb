async function createCategoryDonutChart() {
    try {
        const response = await fetch('/static/statistics/category_total_co2.json');
        const data = await response.json();
        
        // 차트 데이터 준비
        const labels = data.map(item => item.institutionType);
        const values = data.map(item => item.totalMB);
        
        // 통계 정보 계산
        const total = values.reduce((a, b) => a + b, 0);
        const max = Math.max(...values);
        const min = Math.min(...values);
        const avg = total / values.length;
        
       
        // 도넛 차트 생성
        const ctx = document.getElementById('categoryDonutChart').getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: [
                        '#198754',  // 녹색
                        '#28a745',  // 밝은 녹색
                        '#20c997',  // 청록색
                        '#75b798'   // 연한 녹색
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw;
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value.toFixed(2)}MB (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating category donut chart:', error);
    }
}

// 페이지 로드 시 차트 생성
document.addEventListener('DOMContentLoaded', createCategoryDonutChart);