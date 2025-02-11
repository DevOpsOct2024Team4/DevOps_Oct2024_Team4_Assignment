*** Settings ***
Library    SeleniumLibrary
Library    Process

*** Variables ***
${LOGIN_URL}            http://127.0.0.1:5000/login
${BROWSER}    Chrome
${STUDENT_EMAIL}    john.tan.2024@example.edu
${STUDENT_PASSWORD}    Johntan111
${STUDENT_ID}        S1234567A
${NEWSTUDENT_NAME}      Test Student
${NEWSTUDENT_EMAIL}     teststudent@example.com
${NEWSTUDENT_YEAR}      2025
${NEWSTUDENT_PASS}      StudentPass123
${NEWSTUDENT_POINTS}    0
${ADMIN_EMAIL}    hp@np.edu.sg
${ADMIN_PASSWORD}    wizardboy
${INVALID_EMAIL}  john@example.edu
${INVALID_PASSWORD}    Johantan111

*** Test Cases ***
Valid Login Test
    [Documentation]    Test Student login with valid credentials
    Open Browser    ${LOGIN_URL}    ${BROWSER}
    Input Text    id=email    ${STUDENT_EMAIL}
    Input Text    id=password    ${STUDENT_PASSWORD}
    Click Button    id=submit
    Wait Until Element Is Visible    id=student_dashboard    timeout=10
    Page Should Contain    Welcome, John Tan
    Close Browser
Invalid Login Test
    [Documentation]    Test Student login with invalid credentials.
    Open Browser    ${LOGIN_URL}    ${BROWSER}
    Input Text    id=email    ${INVALID_EMAIL}
    Input Text    id=password    ${INVALID_PASSWORD}
    Click Button    id=submit
    Wait Until Element Is Visible    class=error    timeout=15

    # Correct error message based on your app: "Invalid username or password"
    Element Text Should Be    class=error    Invalid username or password

    Close Browser

Valid Redeem Test
    [Documentation]    Test Redemption when student has sufficient points.
    Open Browser    ${LOGIN_URL}    ${BROWSER}
    Input Text    id=email    ${STUDENT_EMAIL}
    Input Text    id=password    ${STUDENT_PASSWORD}
    Click Button    id=submit
    Wait Until Element Is Visible    id=student_dashboard    timeout=10
    Page Should Contain    Welcome, John Tan

    #Redeem Part
     Click Button    id=redeem_item 
     Wait Until Element Is Visible    id=redeem_item    timeout=10
     Page Should Contain    Redemption Successful!
     Close Browser

# Invalid Redemption Test 
#     [Documentation]    Test Redemption when student has insufficient points.
#     Open Browser    ${LOGIN_URL}    ${BROWSER}
#     Input Text    id=email    ${STUDENT_EMAIL}
#     Input Text    id=password    ${STUDENT_PASSWORD}
#     Click Button    id=submit
#     Wait Until Element Is Visible    id=student_dashboard    timeout=10
#     Page Should Contain    Welcome, John Tan
    
#     Click Button    id=redeem_item
#     Wait Until Element Is Visible    class=error    timeout=10
#     Element Text Should Be    class=error    Insufficient points to redeem this item!
#     Close Browser

# Valid Test Cases
#     [Documentation]    Test on whether admin can create student accounts.
#     Open Browser    ${LOGIN_URL}    ${BROWSER}
#     Input Text    id=email    ${ADMIN_EMAIL}
#     Input Text    id=password    ${ADMIN_PASSWORD}
#     Click Button    id=submit
#     Wait Until Element Is Visible    id=admin_dashboard    timeout=10
#     Page Should Contain    Welcome to Admin Dashboard

Valid Delete Item Test
    [Documentation]    Testing whether the admin can delete an item
    Open Browser    ${LOGIN_URL}    ${BROWSER}
    Input Text    id=email    ${ADMIN_EMAIL}
    Input Text    id=password    ${ADMIN_PASSWORD}
    Click Button    id=submit
    Wait Until Element Is Visible    id=admin_dashboard    timeout=10
    Page Should Contain    Welcome to Admin Dashboard
    Close Browser

*** Keywords ***
Send Test Results to Discord
    Run Process    python    send_test_results.py