import database as db
from search import BFS_Spider
import logging
import time

def crawl_website(url, website_name):
    base_url = url
    print(f"Starting crawl for {website_name}: {base_url}")
    
    start_time = time.time()
    
    spider = BFS_Spider(base_url, website_name)
    spider.bfs_search()
    
    end_time = time.time()
    
    elapsed_time = end_time - start_time
    print(f"Finished crawl for {website_name}: {base_url}")
    print(f"Crawling time: {elapsed_time:.2f} seconds")
    
    return elapsed_time

def main():
    url = "https://computer.donga.ac.kr/computer/Main.do"
    website_name = "동아대_test"

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Starting the application...")

    db.connect_to_database()
    
    total_start_time = time.time()
    
    crawling_time = crawl_website(url, website_name)
    
    total_end_time = time.time()
    total_elapsed_time = total_end_time - total_start_time
    
    print(f"\nTotal execution time: {total_elapsed_time:.2f} seconds")
    print(f"Pure crawling time: {crawling_time:.2f} seconds")
    print(f"Overhead time: {(total_elapsed_time - crawling_time):.2f} seconds")
    
    db.disconnect_from_database()

if __name__ == "__main__":
    main()