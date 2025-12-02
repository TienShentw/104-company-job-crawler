import re
import time
import requests
import pandas as pd
from datetime import datetime

# ============================
# 取得 company_id
# ============================
def get_company_id(url):

    # case 1：本來就是公司網址
    if "/company/" in url:
        cid = url.split("/company/")[1].split("?")[0].split("#")[0]
        return cid

    # case 2：是職缺網址
    if "/job/" in url:
        jobNo = url.split("/job/")[1].split("?")[0].split("#")[0]

        api_url = f"https://www.104.com.tw/job/ajax/content/{jobNo}"

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": f"https://www.104.com.tw/job/{jobNo}"
        }

        res = requests.get(api_url, headers=headers)

        try:
            data = res.json()
        except Exception:
            print("⚠ 104 API 被擋，可能缺 Referer 或被封。回傳內容：")
            print(res.text[:200])
            return None

        cust_url = data["data"]["header"]["custUrl"]
        cid = cust_url.split("/company/")[1]
        return cid

    raise ValueError("網址不是 104 公司或職缺頁面")


# ============================
# list → 文字
# ============================
def list_to_text(lst):
    if not lst:
        return ""

    if isinstance(lst, list) and len(lst) > 0:
        # list of string
        if isinstance(lst[0], str):
            return "、".join(lst)

        # list of dict
        if isinstance(lst[0], dict):
            items = []
            for item in lst:
                if "code" in item and "ability" in item:
                    items.append(f"{item['code']}：{item['ability']}")
                else:
                    items.append("、".join([str(v) for v in item.values()]))
            return "、".join(items)

    return str(lst)


# ============================
# 主要爬蟲功能
# ============================
def crawl_company_jobs(url, total_page):

    company_id = get_company_id(url)
    print("✔ company_id =", company_id)

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": f"https://www.104.com.tw/company/{company_id}"
    }

    JobList = pd.DataFrame()

    for page_number in range(1, total_page + 1):

        list_url = f"https://www.104.com.tw/company/ajax/joblist/{company_id}?page={page_number}"
        print(f"\n=== 正在抓取第 {page_number} 頁 ===")

        res = requests.get(list_url, headers=headers).json()

        jobs = res["data"]["list"]["normalJobs"]

        if not jobs:
            print("⚠️ 無更多職缺")
            break

        for job in jobs:

            jobNo = job["encodedJobNo"]
            api_url = f"https://www.104.com.tw/job/ajax/content/{jobNo}"

            print("→ 正在爬取：", api_url)

            try:
                job_json = requests.get(api_url, headers=headers).json()
                data = job_json["data"]

                header = data["header"]
                condition = data["condition"]
                jobdetail = data["jobDetail"]

                row = {
                    "工作職稱": header.get("jobName", ""),
                    "更新日期": header.get("appearDate", ""),
                    "工作內容": jobdetail.get("jobDescription", ""),
                    "工作待遇": jobdetail.get("salary", ""),
                    "上班地點": jobdetail.get("addressRegion", "") + jobdetail.get("addressDetail", ""),

                    "職務類別": jobdetail.get("jobCategory", [{}])[0].get("description", ""),

                    "管理責任": jobdetail.get("manageResp", ""),
                    "出差外派": jobdetail.get("businessTrip", ""),
                    "上班時段": jobdetail.get("workPeriod", ""),
                    "休假制度": jobdetail.get("vacationPolicy", ""),
                    "可上班日": jobdetail.get("startWorkingDay", ""),
                    "需求人數": jobdetail.get("needEmp", ""),

                    "學歷要求": condition.get("edu", ""),
                    "工作經歷": condition.get("workExp", ""),

                    "語文條件": list_to_text(condition.get("language", [])),
                    "擅長工具": list_to_text(condition.get("specialty", [])),
                    "工作技能": list_to_text(condition.get("skill", [])),
                    "具備證照": list_to_text(condition.get("certificate", [])),
                    "科系要求": list_to_text(condition.get("major", [])),

                    "其他條件": condition.get("other", ""),
                    "連結路徑": f"https://www.104.com.tw/job/{jobNo}"
                }

                JobList = pd.concat([JobList, pd.DataFrame([row])], ignore_index=True)
                time.sleep(0.2)

            except Exception as e:
                print("❌ 錯誤：", e)
                time.sleep(1)
                continue

    print("\n🎉 完成，共抓到", len(JobList), "筆資料！")
    return JobList, company_id


# ============================
# 主程式入口
# ============================
if __name__ == "__main__":

    url = input("請貼上 104 公司或職缺網址： ").strip()
    total_page = int(input("請輸入要爬幾頁： "))

    df, cid = crawl_company_jobs(url, total_page)

    # 清公司名（第一次職缺的 header）
    try:
        sample_job_url = f"https://www.104.com.tw/company/ajax/joblist/{cid}?page=1"
        sample = requests.get(sample_job_url, headers={"User-Agent": "Mozilla/5.0"}).json()
        first_job = sample["data"]["list"]["normalJobs"][0]
        jobNo = first_job["encodedJobNo"]

        detail = requests.get(
            f"https://www.104.com.tw/job/ajax/content/{jobNo}",
            headers={"User-Agent": "Mozilla/5.0"}
        ).json()

        company_name = detail["data"]["header"]["custName"]
        company_name = re.sub(r'[<>:"/\\|?*]', '', company_name)

    except:
        company_name = cid

    # 存檔
    current_datetime = datetime.now()
    formatted_date = current_datetime.strftime("%Y-%m-%d-%H%M")

    output_name = f"JobList_{company_name}_{formatted_date}.xlsx"

    df.to_excel(output_name, index=False, encoding="utf-8")
    print(f"📁 檔案已輸出： {output_name}")
