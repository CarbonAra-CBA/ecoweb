 // 페이지 로드 시 비동기 작업 상태 확인 시작
 window.onload = function() {
    document.getElementById('progress-overlay').style.display = 'block';
    document.getElementById('progress-bar').style.display = 'flex';
    // 5초마다 비동기 작업 상태 확인
    window.intervalId = setInterval(checkAsyncResult, 5000);
};

const taskId = "{{ task_id }}";

                // 비동기 작업 결과를 확인하는 함수
                function checkAsyncResult() {
                    fetch(`/check_async/${taskId}`)
                        .then(response => {
                            if (response.status === 200) {
                                return response.json();
                            } else if (response.status === 202) {
                                return { status: 'pending' };
                            } else {
                                throw new Error('알 수 없는 상태');
                            }
                        })
                        .then(data => {
                            if (data.status === 'completed') {
                                const guideline = document.getElementById('guideline-section');

                                // 기존의 "비동기 작업 진행 중..." 메시지를 제거
                                guideline.innerHTML = '';

                                // 비동기 프로그래스 바와 오버레이 숨기기
                                document.getElementById('progress-overlay').style.display = 'none';
                                document.getElementById('progress-bar').style.display = 'none';

                                // data.result는 [{number: , title: , isFellow: }, {}, ..., {}] 형태의 12개 객체 배열
                                data.result.forEach(item => {
                                    // 새로운 테이블 행 생성
                                    const tr = document.createElement('tr');

                                    // Number 열 생성 및 값 설정
                                    const tdNumber = document.createElement('td');
                                    tdNumber.textContent = item.number;
                                    tr.appendChild(tdNumber);

                                    // Title 열 생성 및 값 설정
                                    const tdTitle = document.createElement('td');
                                    tdTitle.textContent = item.title;
                                    tr.appendChild(tdTitle);

                                    // isFellow 열 생성 및 조건에 따라 ✅ 또는 ❌ 설정
                                    const tdIsFellow = document.createElement('td');
                                    tdIsFellow.textContent = item.isFellow === "True" ? "✅" : "❌";
                                    tr.appendChild(tdIsFellow);

                                    // 생성된 행을 tbody에 추가
                                    guideline.appendChild(tr);
                                });

                                clearInterval(intervalId);  // 폴링 중지
                            } else {
                                console.log('비동기 작업 진행 중...');
                            }
                        })
                        .catch(error => {
                            console.error('오류:', error);
                        });
                }

                // 페이지 로드 시 비동기 작업 상태 확인 시작
                window.onload = function() {
                    document.getElementById('progress-overlay').style.display = 'block';
                    document.getElementById('progress-bar').style.display = 'flex';
                    // 5초마다 비동기 작업 상태 확인
                    window.intervalId = setInterval(checkAsyncResult, 5000);
                };