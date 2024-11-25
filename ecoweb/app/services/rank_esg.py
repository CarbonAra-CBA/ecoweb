import pandas as pd 
import json
'''
상위5개 하위5개 웹사이트 추출
'''
def get_top5_sites():
    # CSV 파일 읽기
    df = pd.read_csv('../data/urls/flattened_lighthouse_traffic.csv')
    
    # total 타입만 필터링
    total_df = df[df['resource_summary.resourceType'] == 'total']
    
    # 가장 효율적인(작은) 5개 사이트
    top5_efficient = total_df.nsmallest(5, 'resource_summary.transferSize')[
        ['siteName', 'institutionCategory', 'resource_summary.transferSize']
    ]
    
    # 가장 비효율적인(큰) 5개 사이트
    top5_inefficient = total_df.nlargest(5, 'resource_summary.transferSize')[
        ['siteName', 'institutionCategory', 'resource_summary.transferSize']
    ]
    
    # 결과 출력 (디버깅용)
    print("\n=== 가장 효율적인 웹사이트 TOP 5 ===")
    for idx, row in top5_efficient.iterrows():
        size_kb = row['resource_summary.transferSize'] / 1024
        print(f"{row['siteName']} ({row['institutionCategory']}): {size_kb:.2f}KB")
    
    print("\n=== 가장 비효율적인 웹사이트 TOP 5 ===")
    for idx, row in top5_inefficient.iterrows():
        size_kb = row['resource_summary.transferSize'] / 1024
        print(f"{row['siteName']} ({row['institutionCategory']}): {size_kb:.2f}KB")
    
    # 효율적인 사이트 JSON 저장
    efficient_list = [{
        'siteName': row['siteName'],
        'institutionCategory': row['institutionCategory'],
        'transferSize': float(row['resource_summary.transferSize'] / 1024)
    } for idx, row in top5_efficient.iterrows()]
    
    # 비효율적인 사이트 JSON 저장
    inefficient_list = [{
        'siteName': row['siteName'],
        'institutionCategory': row['institutionCategory'],
        'transferSize': float(row['resource_summary.transferSize'] / 1024)
    } for idx, row in top5_inefficient.iterrows()]
    
    # JSON 파일로 저장 (한글 인코딩 처리)
    with open('../static/statistics/top5_efficient_sites.json', 'w', encoding='utf-8') as f:
        json.dump(efficient_list, f, ensure_ascii=False, indent=2)
    
    with open('../static/statistics/top5_bad_sites.json', 'w', encoding='utf-8') as f:
        json.dump(inefficient_list, f, ensure_ascii=False, indent=2)
    
    return top5_efficient, top5_inefficient

if __name__ == "__main__":
    get_top5_sites()