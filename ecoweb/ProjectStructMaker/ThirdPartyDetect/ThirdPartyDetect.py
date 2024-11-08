def ThirdPartyIgnore(url, url_list):
    # 자주 사용되는 서드 파티 라이브러리 목록 정의
    third_party_resources = [
        {"name": "jQuery", "file": "jquery", "cdn": "https://code.jquery.com/jquery-"},
        {"name": "Chart.js", "file": "chart", "cdn": "https://cdn.jsdelivr.net/npm/chart.js"},
        {"name": "Bootstrap CSS", "file": "bootstrap", "cdn": "https://stackpath.bootstrapcdn.com/bootstrap/"},
        {"name": "Font Awesome", "file": "font-awesome",
         "cdn": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/"},
        # 필요에 따라 추가적인 서드 파티 리소스를 여기에 추가
    ]

    # 서드 파티 리소스를 제외한 URL을 담을 리스트
    non_third_party_resources = []

    for link in url_list:
        # link가 딕셔너리 형태일 때, 'url' 키가 있는지 확인
        link_url = link.get("url") if isinstance(link, dict) else link

        # 서드 파티 리소스 여부 플래그
        is_third_party = False
        link_file = link_url.replace(url, '')  # 주어진 기본 url을 제거하여 상대 경로로 만듦

        # CDN URL 또는 파일명을 기준으로 서드 파티 리소스 여부 확인
        for resource in third_party_resources:
            if resource["file"] in link_file or resource["cdn"] in link_url:
                is_third_party = True
                break

        # 서드 파티 리소스가 아닌 경우 리스트에 추가
        if not is_third_party:
            non_third_party_resources.append(link)

    return non_third_party_resources
