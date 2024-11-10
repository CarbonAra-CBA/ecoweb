function drawInstitutionChart(currentMB, institutionType) {
    const margin = {top: 40, right: 120, bottom: 40, left: 60};
    const width = 1600 - margin.left - margin.right;
    const height = 500 - margin.top - margin.bottom;

    const colors = ['#ff0000', '#0000ff', '#00ff00', '#800080'];
    
    const svg = d3.select("#institution-chart")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    d3.json('/static/js/institution_data.json').then(data => {
        // 모든 데이터 합치기
        let allData = [];
        let currentPosition = 0;
        const boundaries = [0];
        let currentSitePosition;

        data.institutions.forEach((inst, i) => {
            // 현재 기관 타입의 시작 위치 저장
            if (inst.type === institutionType) {
                const sortedSizes = inst.data.map(d => d.size_mb).sort((a, b) => a - b);
                const positionInGroup = sortedSizes.findIndex(size => size >= currentMB);
                currentSitePosition = currentPosition + (positionInGroup === -1 ? inst.data.length : positionInGroup);
            }

            inst.data.forEach(d => {
                allData.push({
                    position: currentPosition++,
                    size_mb: d.size_mb,
                    type: inst.type,
                    color: colors[i]
                });
            });
            boundaries.push(currentPosition);
        });

        // 스케일 설정
        const x = d3.scaleLinear()
            .domain([0, allData.length])
            .range([0, width]);

        const y = d3.scaleLinear()
            .domain([0, d3.max(allData, d => d.size_mb)])
            .range([height, 0]);

        // 막대 그리기
        svg.selectAll("rect")
            .data(allData)
            .enter()
            .append("rect")
            .attr("x", d => x(d.position))
            .attr("y", d => y(d.size_mb))
            .attr("width", width / allData.length)
            .attr("height", d => height - y(d.size_mb))
            .attr("fill", d => d.color);

        // 4.7MB 기준선
        svg.append("line")
            .attr("x1", 0)
            .attr("x2", width)
            .attr("y1", y(4.7))
            .attr("y2", y(4.7))
            .attr("stroke", "black")
            .attr("stroke-dasharray", "5,5");

        // 현재 사이트 위치 표시 (세로선)
        if (currentSitePosition !== undefined) {
            svg.append("line")
                .attr("x1", x(currentSitePosition))
                .attr("x2", x(currentSitePosition))
                .attr("y1", 0)
                .attr("y2", height)
                .attr("stroke", "red")
                .attr("stroke-width", 2);
        }

        // 축 그리기
        svg.append("g")
            .attr("transform", `translate(0,${height})`)
            .call(d3.axisBottom(x));

        svg.append("g")
            .call(d3.axisLeft(y));

        // 기관 구분선과 레이블
        boundaries.slice(0, -1).forEach((boundary, i) => {
            const midPoint = (boundary + boundaries[i + 1]) / 2;
            
            svg.append("line")
                .attr("x1", x(boundary))
                .attr("x2", x(boundary))
                .attr("y1", 0)
                .attr("y2", height)
                .attr("stroke", "gray")
                .attr("stroke-dasharray", "2,2");

            svg.append("text")
                .attr("x", x(midPoint))
                .attr("y", -10)
                .attr("text-anchor", "middle")
                .text(data.institutions[i].type);
        });

        // 범례 추가
        const legendItems = [
            {color: "red", text: `현재 사이트 (${currentMB.toFixed(2)}MB)`, dash: "0"},
            {color: "black", text: "대한민국 평균선(4.7MB)", dash: "5,5"}
        ];

        const legend = svg.append("g")
            .attr("transform", `translate(${width - 200}, 20)`);

        legendItems.forEach((item, i) => {
            const g = legend.append("g")
                .attr("transform", `translate(0, ${i * 20})`);
                
            g.append("line")
                .attr("x1", 0)
                .attr("x2", 20)
                .attr("y1", 0)
                .attr("y2", 0)
                .attr("stroke", item.color)
                .attr("stroke-width", 2)
                .attr("stroke-dasharray", item.dash);
                
            g.append("text")
                .attr("x", 25)
                .attr("y", 5)
                .text(item.text);
        });
    });
}