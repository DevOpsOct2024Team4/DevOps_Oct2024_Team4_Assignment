*** Settings ***
Library    SeleniumLibrary
Library    Process
Suite Setup    Open Browser    http://127.0.0.1:5000/login    Chrome
Suite Teardown    Close Browser

*** Variables ***
${STUDENT_EMAIL}    john.tan.2024@example.edu
${STUDENT_PASSWORD}    Johntan222
${INVALID_EMAIL}    invalid@example.com
${INVALID_PASSWORD}    wrongpass
${ITEM_NAME}    Book

*** Test Cases ***

*** Settings ***
Library    SeleniumLibrary

*** Variables ***
${URL}       http://127.0.0.1:5000
${BROWSER}   Chrome
${STUDENT_EMAIL}    john.tan.2024@example.edu
${STUDENT_PASSWORD}  Johntan222

*** Test Cases ***
Student Login Successful
    [Documentation]    Verify that a student can successfully log in with valid credentials.
    Open Browser    ${URL}/login    ${BROWSER}
    Maximize Browser Window
    Wait Until Element Is Visible    id=email    timeout=5s
    Input Text    id=email    ${STUDENT_EMAIL}
    Input Text    id=password    ${STUDENT_PASSWORD}
    Click Button    xpath=//button[@type='submit']
    Wait Until Page Contains    Welcome, John Tan!
    [Teardown]    Close Browser

Student Login Failed
    [Documentation]    Verify that login fails with invalid student credentials.
    Open Browser    ${URL}/login    ${BROWSER}
    Maximize Browser Window
    Wait Until Element Is Visible    id=email    timeout=5s
    Input Text    id=email    wrong.email@example.edu
    Input Text    id=password    wrongpassword
    Click Button    xpath=//button[@type='submit']
    Wait Until Page Contains    Invalid email or password.
    [Teardown]    Close Browser

*** Test Cases ***

# ✅ Test Case 1: Successful Redemption
Redeem Item Successfully
    [Documentation]    Verify that a student can redeem an item successfully.
    Open Browser    ${URL}/login    ${BROWSER}
    Maximize Browser Window
    Wait Until Element Is Visible    name=Email    timeout=10s
    Input Text    name=Email    ${STUDENT_EMAIL}
    Input Text    name=Password    ${STUDENT_PASSWORD}
    Click Button    xpath=//button[@type='submit']
    Wait Until Page Contains    Welcome, John Tan!

    # Step 1: Redeem the Item
    Wait Until Element Is Visible    xpath=//button[contains(., 'Redeem') and ancestor::li[contains(., '${ITEM_NAME}')]]
    Click Button    xpath=//button[contains(., 'Redeem') and ancestor::li[contains(., '${ITEM_NAME}')]]

    # Step 2: Verify Redemption Success
    Wait Until Page Contains    Redemption Successful!
    Page Should Contain    Points Left:
    Close Browser

# ❌ Test Case 2: Redemption Failure (Insufficient Points)
Redeem Item Failure Due to Insufficient Points
    [Documentation]    Verify that a student cannot redeem an item if they do NOT have enough points.
    Open Browser    ${URL}/login    ${BROWSER}
    Maximize Browser Window
    Wait Until Element Is Visible    name=Email    timeout=10s
    Input Text    name=Email    ${STUDENT_EMAIL}
    Input Text    name=Password    ${STUDENT_PASSWORD}
    Click Button    xpath=//button[@type='submit']
    Wait Until Page Contains    Welcome, John Tan!

    # Step 1: Attempt to Redeem
    Wait Until Element Is Visible    xpath=//button[contains(., 'Redeem') and ancestor::li[contains(., '${ITEM_NAME}')]]
    Click Button    xpath=//button[contains(., 'Redeem') and ancestor::li[contains(., '${ITEM_NAME}')]]

    # Step 2: Verify Failure Message
    Wait Until Page Contains    Insufficient points or item out of stock!
    Page Should Contain    Insufficient points or item out of stock!
    Close Browser

*** Keywords ***
Send Test Results to Discord
    Run Process    python    send_test_results.py