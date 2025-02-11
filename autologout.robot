*** Settings ***
Library    SeleniumLibrary
Library    Process

*** Variables ***
${URL}    http://127.0.0.1:5000/login
${ADMIN_EMAIL}    hp@np.edu.sg
${ADMIN_PASSWORD}    wizardboy
${TIMEOUT}    125

*** Test Cases ***
Verify Auto Logout After Inactivity
    # Step 1: Login as Admin
    Open Browser    ${URL}    Chrome
    Input Text    id=email    ${ADMIN_EMAIL}
    Input Text    id=password    ${ADMIN_PASSWORD}
    Click Button    xpath=//button[@type='submit']
    Wait Until Page Contains    Admin Dashboard

    # Step 2: Wait for Session Timeout
    Sleep    ${TIMEOUT}    # Wait for the session to expire (adjust based on timeout setting)

    # Step 3: Verify Logout
    Page Should Contain    You have been logged out.

    # Step 4: Send Discord Notification
    Run Process    python    send_test_results.py    Auto-logout test completed successfully.

    # Step 5: Close Browser
    Close Browser