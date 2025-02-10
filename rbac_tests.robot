*** Settings ***
Library    SeleniumLibrary

*** Variables ***
${BROWSER}          Chrome
${URL}              http://127.0.0.1:5000
${ADMIN_EMAIL}    hp@np.edu.sg
${ADMIN_PASSWORD}    wizardboy
${STUDENT_EMAIL}    john.tan.2024@example.edu
${STUDENT_PASSWORD}    Johntan222

*** Test Cases ***

# Test Case 1: Admin Can Access Admin Dashboard
Admin Can Access Admin Dashboard
    [Documentation]    Verify that the admin can log in and access the admin dashboard.
    Open Browser    ${URL}/login    ${BROWSER}
    Input Text    name=Email    ${ADMIN_EMAIL}
    Input Text    name=Password    ${ADMIN_PASSWORD}
    Click Button    xpath=//button[@type='submit']
    Wait Until Page Contains    Admin Dashboard
    Title Should Be    Admin Dashboard
    [Teardown]    Close Browser


# Test Case 2: Student Can Access Their Dashboard
Student Can Access Their Dashboard
    [Documentation]    Verify that the student can log in and access their dashboard.
    Open Browser    ${URL}/login    ${BROWSER}
    Input Text    name=Email    ${STUDENT_EMAIL}
    Input Text    name=Password    ${STUDENT_PASSWORD}
    Click Button    xpath=//button[@type='submit']
    Wait Until Page Contains    Redeemable Items
    Title Should Be    Student Dashboard
    [Teardown]    Close Browser


# Test Case 3: Prevent Student from Accessing Admin Dashboard
Student Cannot Access Admin Dashboard
    [Documentation]    Ensure that students cannot access the admin dashboard.
    Open Browser    ${URL}/login    ${BROWSER}
    Input Text    name=Email    ${STUDENT_EMAIL}
    Input Text    name=Password    ${STUDENT_PASSWORD}
    Click Button    xpath=//button[@type='submit']
    Go To    ${URL}/admin
    Wait Until Page Contains    Access denied: Admins only!
    [Teardown]    Close Browser


# Test Case 4: Invalid Login Attempt
Invalid Login Attempt
    [Documentation]    Verify that invalid login credentials are not accepted.
    Open Browser    ${URL}/login    ${BROWSER}
    Input Text    name=Email    fakeuser@example.com
    Input Text    name=Password    wrongpassword123
    Click Button    xpath=//button[@type='submit']
    Wait Until Page Contains    Invalid email or password.
    [Teardown]    Close Browser
