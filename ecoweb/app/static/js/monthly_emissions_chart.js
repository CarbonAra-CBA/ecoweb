function createMonthlyEmissionsChart() {
    // 현재 날짜 기준으로 이전 12개월 라벨 생성
    const months = [];
    const data = [];
    const currentDate = new Date();
    
    for (let i = 11; i >= 0; i--) {
        const d = new Date(currentDate.getFullYear(), currentDate.getMonth() - i, 1);
        months.push(d.toLocaleString('ko-KR', { month: 'short' }));
        
        // 1.5~2.0 사이의 랜덤값 생성 (시뮬레이션) 
        const randomEmission = 1.5 + (Math.random() * 0.5);
        data.push(randomEmission.toFixed(2));
    }

    const ctx = document.getElementById('monthlyEmissionsChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,
            datasets: [{
                label: '월별 탄소 배출량',
                data: data,
                borderColor: '#198754',
                backgroundColor: 'rgba(25, 135, 84, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `탄소 배출량: ${context.raw}g CO₂`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    min: 1.4,  // y축 최소값
                    max: 2.1,  // y축 최대값
                    ticks: {
                        callback: function(value) {
                            return value.toFixed(2) + 'g';
                        }
                    },
                    title: {
                        display: true,
                        text: '탄소 배출량 (g CO₂)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: '월'
                    }
                }
            }
        }
    });
}

// 페이지 로드 시 차트 생성
document.addEventListener('DOMContentLoaded', createMonthlyEmissionsChart);