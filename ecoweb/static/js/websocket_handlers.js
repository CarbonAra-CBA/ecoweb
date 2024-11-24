const socket = io();

socket.on('connect' , () => { 
    console.log('WebSocket connected');
})

socket.on('carbon_result', (data) => {
    if (data.status === 'success') {
        // 결과 업데이트 UI 로직
        document.getElementById('carbon-result').innerHTML = `
            <h3>탄소 배출량: ${data.carbon_emission} g</h3>
            <p>총 용량: ${data.kb_weight} KB</p>
        `;
    }
});