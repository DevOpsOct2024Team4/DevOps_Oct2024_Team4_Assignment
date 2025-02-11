*** Settings ***
Library    SeleniumLibrary
Suite Setup    Open Browser    http://127.0.0.1:5000/login    Chrome
Suite Teardown    Close Browser

*** Variables ***
${STUDENT_EMAIL}    john.tan.2024@example.edu
${STUDENT_PASSWORD}    Johntan222
${INVALID_EMAIL}    invalid@example.com
${INVALID_PASSWORD}    wrongpass

*** Test Cases ***

*** Settings ***
Library    SeleniumLibrary

*** Variables ***
${URL}       http://127.0.0.1:5000/login
${BROWSER}   Chrome
${STUDENT_EMAIL}    john.tan.2024@example.edu
${STUDENT_PASSWORD}  Johntan222

*** Test Cases ***
Student Login Successful
    [Documentation]    Verify that a student can successfully log in with valid credentials.
    Open Browser    ${URL}    ${BROWSER}
    Maximize Browser Window
    Wait Until Element Is Visible    id=email    timeout=5s
    Input Text    id=email    ${STUDENT_EMAIL}
    Input Text    id=password    ${STUDENT_PASSWORD}
    Click Button    xpath=//button[@type='submit']
    Wait Until Page Contains    Welcome, John Tan!
    [Teardown]    Close Browser

Student Login Failed
    [Documentation]    Verify that login fails with invalid student credentials.
    Open Browser    ${URL}    ${BROWSER}
    Maximize Browser Window
    Wait Until Element Is Visible    id=email    timeout=5s
    Input Text    id=email    wrong.email@example.edu
    Input Text    id=password    wrongpassword
    Click Button    xpath=//button[@type='submit']
    Wait Until Page Contains    Invalid email or password.
    [Teardown]    Close Browser


# Valid Redeem Test
#     [Documentation]    Test Redemption when student has sufficient points.
#     Open Browser    ${LOGIN_URL}    ${BROWSER}
#     Input Text    id=email    ${STUDENT_EMAIL}
#     Input Text    id=password    ${STUDENT_PASSWORD}
#     Click Button    id=submit
#     Wait Until Element Is Visible    id=student_dashboard    timeout=10
#     Page Should Contain    Welcome, John Tan

#     #Redeem Part
#      Click Button    id=redeem_item 
#      Wait Until Element Is Visible    id=redeem_item    timeout=10
#      Page Should Contain    Redemption Successful!
#      Close Browser

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

# Valid Delete Item Test
#     [Documentation]    Testing whether the admin can delete an item
#     Open Browser    ${LOGIN_URL}    ${BROWSER}
#     Input Text    id=email    ${ADMIN_EMAIL}
#     Input Text    id=password    ${ADMIN_PASSWORD}
#     Click Button    id=submit
#     Wait Until Element Is Visible    id=admin_dashboard    timeout=10
#     Page Should Contain    Welcome to Admin Dashboard
#     Close Browser

*** Keywords ***
# Send Test Results to Discord
#     Run Process    python    send_test_results.py