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
${URL}       http://127.0.0.1:5000
${BROWSER}   Chrome
${ADMIN_EMAIL}    hp@np.edu.sg
${ADMIN_PASSWORD}    wizardboy

# New Variables for Student Creation
${NEW_STUDENT_ID}        A1234567T
${NEW_STUDENT_NAME}      TEST124
${NEW_STUDENT_EMAIL}     test124@example.com
${NEW_ENTRY_YEAR}        2025
${NEW_DIPLOMA_STUDY}     Information Technology
${NEW_STUDENT_PASSWORD}  Testing124
${NEW_STUDENT_POINTS}    0

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

*** Test Cases ***
Admin Login Successful
    [Documentation]    Verify that an admin can log in with valid credentials.
    Open Browser    ${URL}/login    ${BROWSER}
    Maximize Browser Window
    Wait Until Page Contains Element    xpath=//form[@action='/login']    timeout=15s
    Input Text    name=Email    ${ADMIN_EMAIL}
    Input Text    name=Password    ${ADMIN_PASSWORD}
    Click Button    xpath=//button[@type='submit']
    Wait Until Page Contains    Welcome to the Admin Dashboard
    [Teardown]    Close Browser

Admin Login Failed
    [Documentation]    Verify that login fails with invalid admin credentials.
    Open Browser    ${URL}/login    ${BROWSER}
    Maximize Browser Window
    Wait Until Page Contains Element    xpath=//form[@action='/login']    timeout=15s
    Input Text    name=Email    wrong.admin@example.com
    Input Text    name=Password    wrongpassword
    Click Button    xpath=//button[@type='submit']
    Wait Until Page Contains    Invalid email or password.
    [Teardown]    Close Browser

# ✅ Test Case: Successful Student Account Creation
Create Student Account Successfully
    [Documentation]    Verify that an admin can create a new student account successfully.
    Maximize Browser Window

    # Login as Admin
    Input Text    id=email    ${ADMIN_EMAIL}
    Input Text    id=password    ${ADMIN_PASSWORD}
    Click Button    xpath=//button[@type='submit']
    Wait Until Page Contains    Welcome to the Admin Dashboard

    # Navigate to Create Student Page
    Click Link    xpath=//a[contains(@href, '/admin/create-student')]
    Wait Until Page Contains    Create New Student Account

    # Fill the Create Student Form
    Input Text    name=student_id       ${NEW_STUDENT_ID}
    Input Text    name=student_name     ${NEW_STUDENT_NAME}
    Input Text    name=email            ${NEW_STUDENT_EMAIL}
    Input Text    name=entry_year       ${NEW_ENTRY_YEAR}
    Input Text    name=diploma_study    ${NEW_DIPLOMA_STUDY}
    Input Text    name=password         ${NEW_STUDENT_PASSWORD}
    Input Text    name=points           ${NEW_STUDENT_POINTS}

    # Submit the Form
    Click Button    xpath=//button[@type='submit']
    Wait Until Page Contains    Student account created successfully!    timeout=10s

    [Teardown]    Close Browser

# ❌ Test Case: Failure (Missing Required Fields)
Create Student Account Failure (Missing Fields)
    [Documentation]    Verify that the system prevents student account creation if required fields are missing.
    Maximize Browser Window

    # Login as Admin
    Input Text    id=email    ${ADMIN_EMAIL}
    Input Text    id=password    ${ADMIN_PASSWORD}
    Click Button    xpath=//button[@type='submit']
    Wait Until Page Contains    Welcome to the Admin Dashboard

    # Navigate to Create Student Page
    Click Link    xpath=//a[contains(@href, '/admin/create-student')]
    Wait Until Page Contains    Create New Student Account

    # Leave required fields empty (Missing Student Name & Email)
    Input Text    name=student_id       MISSING001
    Input Text    name=entry_year       ${NEW_ENTRY_YEAR}
    Input Text    name=diploma_study    ${NEW_DIPLOMA_STUDY}
    Input Text    name=password         ${NEW_STUDENT_PASSWORD}
    Input Text    name=points           ${NEW_STUDENT_POINTS}

    # Submit the Form
    Click Button    xpath=//button[@type='submit']

    # Verify Error Message for Missing Fields
    Wait Until Page Contains    This field is required.    timeout=10s

    [Teardown]    Close Browser

*** Keywords ***
Send Test Results to Discord
    Run Process    python    send_test_results.py