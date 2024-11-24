import pandas as pd
import json

def get_category_total_co2():
    # CSV 파일 읽기
    df = pd.read_csv('../data/urls/flattened_lighthouse_traffic.csv')
    
    # total 타입만 필터링
    total_df = df[df['resource_summary.resourceType'] == 'total']
    
    # institutionType 별로 그룹화, 그리고 그룹별로 합계 계산
    total_sites = total_df.groupby('institutionType')['resource_summary.transferSize'].sum()
    
    # byte를 mb로 변환 
    total_sites = (total_sites / 1024 / 1024).round(2)
    
    # Series를 딕셔너리로 변환
    result_dict = total_sites.to_dict()
    
    # 결과 출력 (디버깅용)
    print("\n=== 기관 유형별 총 트래픽 ===")
    for institution_type, mb_size in result_dict.items():
        print(f"{institution_type}: {mb_size}MB")
    
    # JSON 파일로 저장
    result_list = [
        {
            "institutionType": inst_type,
            "totalMB": mb_size
        }
        for inst_type, mb_size in result_dict.items()
    ]
    
    # JSON 파일로 저장 (한글 인코딩 처리)
    with open('../static/statistics/category_total_co2.json', 'w', encoding='utf-8') as f:
        json.dump(result_list, f, ensure_ascii=False, indent=2)
    
    return total_sites

if __name__ == '__main__':
    get_category_total_co2()