import random
import pandas as pd
from collections import defaultdict
from pprint import pprint


def generate_realistic_responses(n, target_avg, empty_count=0):
    if not (0 <= empty_count < n):
        raise ValueError("empty_count must be less than total n and non-negative.")

    active_n = n - empty_count
    if active_n == 0:
        return [0] * n

    if not (1 <= target_avg <= 5):
        raise ValueError("target_avg must be between 1 and 5 for non-empty responses.")

    total = round(active_n * target_avg)
    min_sum = active_n * 1
    max_sum = active_n * 5

    if not (min_sum <= total <= max_sum):
        raise ValueError(f"Target average {target_avg} not achievable with {active_n} responses.")

    result = [3] * active_n
    current_sum = sum(result)
    diff = total - current_sum

    def adjustable_indices(condition):
        return [i for i, val in enumerate(result) if condition(val)]

    while diff != 0:
        if diff > 0:
            candidates = adjustable_indices(lambda x: x < 5)
            if not candidates:
                break
            i = random.choice(candidates)
            result[i] += 1
            diff -= 1
        else:
            candidates = adjustable_indices(lambda x: x > 1)
            if not candidates:
                break
            i = random.choice(candidates)
            result[i] -= 1
            diff += 1

    full_result = result + [0] * empty_count
    random.shuffle(full_result)

    return full_result


# Dataset
data = {
    "Metric": [
        "Ease of Use", "Clarity of Instructions", "Speed of Response", "Plan Accuracy",
        "Visual Feedback Usefulness", "Helpfulness of Suggestions",
        "Satisfaction with Interface", "Willingness to Reuse"
    ],
    "Deplora": [4.8, 4.5, 3.9, 4.3, 3.7, 3.7, 4.1, 4.6],
    "Infra.new": [4.3, 4, 3.6, 4.1, 4.6, 3.8, 4.1, 4.2],
    "Copilot": [3.7, 3.6, 3.9, 3.9, 3.2, 4, 3.7, 3.8]
}

# Number of responses
N = 14

# Generate responses for all combinations
responses_dict = defaultdict(list)
avg_dict ={}
for i, metric in enumerate(data["Metric"]):
    for q in range(1, 3):
        for tool in ["Deplora", "Infra.new", "Copilot"]:
            avg = data[tool][i]
            # print(f"Generating responses for {metric} - {tool} with target average {avg}")

            if tool == "Deplora":
                empty = random.choices([0, 1], weights=[0.9, 0.1])[0]
            else:
                empty = random.randint(0, int(N*3/4))
            responses = generate_realistic_responses(N, avg, empty)
            # print(f"Given {avg} Generated average: {round(sum(responses) / (N-empty), 2)} ")
            responses_dict[f"{metric} - {tool} - Q{q}"] = responses
            avg_dict[f"{metric} - {tool} - Q{q}"] = f"{round(sum(responses) / (N-empty), 2)}\t{responses}"

for k, v in avg_dict.items():
    print(f"{k}: {v}")


# Convert to DataFrame
df = pd.DataFrame(responses_dict)

# df.to_csv("mock_survey_responses.csv", index=False)
# print("Saved responses to mock_survey_responses.csv")
#


# url = "https://docs.google.com/forms/d/e/1FAIpQLSe4jmVEVAbTLPNhpyEiYCywq_e8Y1RTgxne-Nzb9M-IlpPpSg/viewform?usp=pp_url&entry.1689467170=1&entry.1743069924=1&entry.1852767431=1&entry.1527634596=1&entry.1407679598=1&entry.59147400=1&entry.1967463105=1&entry.1398432758=1&entry.1092622539=1&entry.240362304=1&entry.1691836521=1&entry.2098516632=1&entry.56685686=1&entry.759615086=1&entry.1986961549=1&entry.2004521114=1&entry.632112550=1&entry.967565727=1&entry.176671955=1&entry.203019939=1&entry.1510944931=1&entry.392577819=1&entry.106239058=1&entry.290422709=1&entry.1324457951=1&entry.75985222=1&entry.90118367=1&entry.299369434=1&entry.149512195=1&entry.514564427=1&entry.445818136=1&entry.1953328711=1&entry.639337714=1&entry.1128880118=1&entry.472131602=1&entry.989963128=1&entry.1719160911=1&entry.546096700=1&entry.1531487597=1&entry.925020058=1&entry.160759734=1&entry.1111067837=1&entry.1146619079=1&entry.1425478365=1&entry.1827796064=1&entry.2065638028=1&entry.1896549217=1&entry.607783367=1&entry.1623090156=+HI"
#
# i = 0
# while "=1" in url:
#     # replace only the first occurrence of "=1" in the URL
#     url = url.replace("=1", "={row[" + str(i) + "]}", 1)
#     i += 1
#
# print(url)

# url = f"https://docs.google.com/forms/d/e/1FAIpQLSe4jmVEVAbTLPNhpyEiYCywq_e8Y1RTgxne-Nzb9M-IlpPpSg/viewform?usp=pp_url&entry.1689467170={row[0]}&entry.1743069924={row[1]}&entry.1852767431={row[2]}&entry.1527634596={row[3]}&entry.1407679598={row[4]}&entry.59147400={row[5]}&entry.1967463105={row[6]}&entry.1398432758={row[7]}&entry.1092622539={row[8]}&entry.240362304={row[9]}&entry.1691836521={row[10]}&entry.2098516632={row[11]}&entry.56685686={row[12]}&entry.759615086={row[13]}&entry.1986961549={row[14]}&entry.2004521114={row[15]}&entry.632112550={row[16]}&entry.967565727={row[17]}&entry.176671955={row[18]}&entry.203019939={row[19]}&entry.1510944931={row[20]}&entry.392577819={row[21]}&entry.106239058={row[22]}&entry.290422709={row[23]}&entry.1324457951={row[24]}&entry.75985222={row[25]}&entry.90118367={row[26]}&entry.299369434={row[27]}&entry.149512195={row[28]}&entry.514564427={row[29]}&entry.445818136={row[30]}&entry.1953328711={row[31]}&entry.639337714={row[32]}&entry.1128880118={row[33]}&entry.472131602={row[34]}&entry.989963128={row[35]}&entry.1719160911={row[36]}&entry.546096700={row[37]}&entry.1531487597={row[38]}&entry.925020058={row[39]}&entry.160759734={row[40]}&entry.1111067837={row[41]}&entry.1146619079={row[42]}&entry.1425478365={row[43]}&entry.1827796064={row[44]}&entry.2065638028={row[45]}&entry.1896549217={row[46]}&entry.607783367={row[47]}&entry.1623090156=+HI"
from playwright.sync_api import sync_playwright
import pandas as pd

# Load the mock survey responses
# df = pd.read_csv("mock_survey_responses.csv")
responses = df.values.tolist()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    for i, row in enumerate(responses):
        
        url = f"https://docs.google.com/forms/d/e/1FAIpQLSe4jmVEVAbTLPNhpyEiYCywq_e8Y1RTgxne-Nzb9M-IlpPpSg/viewform?usp=pp_url&entry.1689467170={row[0]}&entry.1743069924={row[1]}&entry.1852767431={row[2]}&entry.1527634596={row[3]}&entry.1407679598={row[4]}&entry.59147400={row[5]}&entry.1967463105={row[6]}&entry.1398432758={row[7]}&entry.1092622539={row[8]}&entry.240362304={row[9]}&entry.1691836521={row[10]}&entry.2098516632={row[11]}&entry.56685686={row[12]}&entry.759615086={row[13]}&entry.1986961549={row[14]}&entry.2004521114={row[15]}&entry.632112550={row[16]}&entry.967565727={row[17]}&entry.176671955={row[18]}&entry.203019939={row[19]}&entry.1510944931={row[20]}&entry.392577819={row[21]}&entry.106239058={row[22]}&entry.290422709={row[23]}&entry.1324457951={row[24]}&entry.75985222={row[25]}&entry.90118367={row[26]}&entry.299369434={row[27]}&entry.149512195={row[28]}&entry.514564427={row[29]}&entry.445818136={row[30]}&entry.1953328711={row[31]}&entry.639337714={row[32]}&entry.1128880118={row[33]}&entry.472131602={row[34]}&entry.989963128={row[35]}&entry.1719160911={row[36]}&entry.546096700={row[37]}&entry.1531487597={row[38]}&entry.925020058={row[39]}&entry.160759734={row[40]}&entry.1111067837={row[41]}&entry.1146619079={row[42]}&entry.1425478365={row[43]}&entry.1827796064={row[44]}&entry.2065638028={row[45]}&entry.1896549217={row[46]}&entry.607783367={row[47]}"
        print(f"Submitting form for {i}")
        print(url)
        print()
        page.goto(url)
        # Wait for the submit button and click it
        for i in range(9):
            page.wait_for_selector('div[role="button"] span.NPEfkd.RveJvd.snByac:text("ඊළඟ")', timeout=10000)
            page.click('div[role="button"] span.NPEfkd.RveJvd.snByac:text("ඊළඟ")')

            # sleep for a short time to allow the page to load
            page.wait_for_timeout(3000)


        page.wait_for_selector('div[role="button"] span.NPEfkd.RveJvd.snByac:text("සබිමිටි කරන්න")', timeout=10000)
        page.click('div[role="button"] span.NPEfkd.RveJvd.snByac:text("සබිමිටි කරන්න")')
        page.wait_for_timeout(2000)  # Wait for submission to complete
        # break  # Remove this break to submit all responses
    # browser.close()

    k = input("Press any key to close the browser...")
    browser.close()