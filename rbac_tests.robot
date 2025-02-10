*** Settings ***
Library    SeleniumLibrary
Library    Process
Suite Teardown    Run Keyword    Send Test Results to Discord

*** Variables ***
${URL}    http://127.0.0.1:5000
${BROWSER}    Chrome
${ADMIN_EMAIL}    hp@np.edu.sg
${ADMIN_PASSWORD}    wizardboy
${STUDENT_EMAIL}    john.tan.2024@example.edu
${STUDENT_PASSWORD}    Johntan222

*** Test Cases ***
Admin Can Access Admin Dashboard
    Open Browser    ${URL}/login    ${BROWSER}
    Input Text    name=Email    ${ADMIN_EMAIL}
    Input Text    name=Password    ${ADMIN_PASSWORD}
    Click Button    xpath=//button[@type='submit']
    Wait Until Page Contains    Welcome to the Admin Dashboard
    [Teardown]    Close Browser

Student Can Access Their Dashboard
    Open Browser    ${URL}/login    ${BROWSER}
    Input Text    name=Email    ${STUDENT_EMAIL}
    Input Text    name=Password    ${STUDENT_PASSWORD}
    Click Button    xpath=//button[@type='submit']
    Wait Until Page Contains    Welcome to the Student Dashboard
    [Teardown]    Close Browser

Student Cannot Access Admin Dashboard
    Open Browser    ${URL}/login    ${BROWSER}
    Input Text    name=Email    ${STUDENT_EMAIL}
    Input Text    name=Password    ${STUDENT_PASSWORD}
    Click Button    xpath=//button[@type='submit']
    Go To    ${URL}/admin
    Wait Until Page Contains    Access denied: Admins only!
    [Teardown]    Close Browser

Admin Cannot Access Student Dashboard
    Open Browser    ${URL}/login    ${BROWSER}
    Input Text    name=Email    ${ADMIN_EMAIL}
    Input Text    name=Password    ${ADMIN_PASSWORD}
    Click Button    xpath=//button[@type='submit']
    Go To    ${URL}/student/A1234567X
    Wait Until Page Contains    Unauthorized Access
    [Teardown]    Close Browser

Invalid Login Attempt
    Open Browser    ${URL}/login    ${BROWSER}
    Input Text    name=Email    invalid@example.com
    Input Text    name=Password    invalidpassword
    Click Button    xpath=//button[@type='submit']
    Wait Until Page Contains    Invalid email or password
    [Teardown]    Close Browser

*** Keywords ***
Send Test Results to Discord
    Run Process    python    send_test_results.py

