*** Settings ***
Library    SeleniumLibrary
Library    Process

*** Variables ***
${URL}    http://127.0.0.1:5000
${BROWSER}    Chrome
${ADMIN_EMAIL}    hp@np.edu.sg
${ADMIN_PASSWORD}    wizardboy
${STUDENT_ID}    S1234441A
${NEW_NAME}    Hulk Updated
${NEW_EMAIL}    hulksmash@np.edu.sg
${NEW_POINTS}    150
${NEW_YEAR}    2023

*** Test Cases ***
Modify Student Information
    [Documentation]    Verify that an admin can modify a student's details successfully.
    
    # Step 1: Login as Admin
    Open Browser    ${URL}/login    ${BROWSER}
    Input Text    name=Email    ${ADMIN_EMAIL}
    Input Text    name=Password    ${ADMIN_PASSWORD}
    Click Button    xpath=//button[@type='submit']
    Wait Until Page Contains    Admin Dashboard

    # Step 2: Navigate to Student List
    Click Link    xpath=//a[contains(@href, '/admin/list-students')]
    Wait Until Page Contains    Student List

    # Step 3: Modify the Student
    # This finds the row with 'Hulk' and clicks the corresponding 'Modify' link
    Click Element    xpath=//tr[td[contains(text(), 'Hulk')]]//a[contains(@href, 'modify-student')]
    Input Text    name=student_name    ${NEW_NAME}
    Input Text    name=email    ${NEW_EMAIL}
    Click Button    xpath=//button[@type='submit']

    # Step 4: Verify Update in Student List
    Wait Until Page Contains    Student List
    Page Should Contain    ${NEW_NAME}
    Page Should Contain    ${NEW_EMAIL}

    # Step 5: Send Discord Notification
    Run Process    python    send_test_results.py    "✅ Student ${NEW_NAME} successfully modified."
    Close Browser


