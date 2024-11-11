def ThirdPartyIgnore(url_list):
    # 자주 사용되는 서드 파티 라이브러리 목록 정의
    third_party_resources = [
        "jquery", "swiper", "react", "React", "Angular", "Vue", "D3", "Axios", "Lodash", "Moment", "animate", "slick"
        # 필요에 따라 추가적인 서드 파티 리소스를 여기에 추가
    ]

    # 서드 파티 리소스를 제외한 URL을 담을 리스트
    non_third_party_resources = []

    for link in url_list:
        # "url" 키에서 URL을 가져옴
        url = link.get("url", "")

        # 서드 파티 리소스가 포함되어 있지 않다면 리스트에 추가
        if not any(resource.lower() in url.lower() for resource in third_party_resources):
            non_third_party_resources.append(link)

    return non_third_party_resources
