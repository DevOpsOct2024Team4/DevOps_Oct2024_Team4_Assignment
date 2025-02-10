import xml.etree.ElementTree as ET
import requests

# Path to the Robot Framework output file
OUTPUT_FILE = 'output.xml'

# Discord webhook URL (replace with your actual webhook URL)
WEBHOOK_URL = 'https://discord.com/api/webhooks/1338542484036386969/16kfW53a89Nu-a-MWf5Q8Rmfog8iS_My6PQkeVY8kRNf01Amt3n6-JAtWIE-XgnK7tGL'

def parse_test_results(output_file):
    tree = ET.parse(output_file)
    root = tree.getroot()

    total_tests = 0
    passed_tests = 0
    failed_tests = 0

    for suite in root.findall('.//suite'):
        for test in suite.findall('test'):
            total_tests += 1
            status = test.find('status').attrib['status']
            if status == 'PASS':
                passed_tests += 1
            elif status == 'FAIL':
                failed_tests += 1

    return total_tests, passed_tests, failed_tests

def send_discord_notification(total, passed, failed):
    message = f"🧪 **Test Results Summary:**\n✅ Passed: {passed}\n❌ Failed: {failed}\n📊 Total: {total}"
    payload = {"content": message}
    requests.post(WEBHOOK_URL, json=payload)

if __name__ == "__main__":
    total, passed, failed = parse_test_results(OUTPUT_FILE)
    send_discord_notification(total, passed, failed)
