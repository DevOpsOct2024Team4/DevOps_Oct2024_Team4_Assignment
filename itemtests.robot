*** Settings ***
Library    SeleniumLibrary
Library    OperatingSystem
Library    Process

*** Variables ***
${URL}    http://127.0.0.1:5000/login
${ADMIN_EMAIL}    hp@np.edu.sg
${ADMIN_PASSWORD}    wizardboy
${ITEM_NAME}    Test Item
${UPDATED_NAME}    Updated Item
${ITEM_QUANTITY}    10
${UPDATED_QUANTITY}    20
${ITEM_VALUE}    50
${UPDATED_VALUE}    75

*** Test Cases ***
Create, Modify, and Delete Item with Discord Notification
    # Step 1: Login as Admin
    Open Browser    ${URL}    Chrome
    Input Text    id=email    ${ADMIN_EMAIL}
    Input Text    id=password    ${ADMIN_PASSWORD}
    Click Button    xpath=//button[@type='submit']
    Wait Until Page Contains    Admin Dashboard

    # Step 2: Create New Item
    Go To    http://127.0.0.1:5000/admin/manage-items
    Input Text    name=item_id    test123
    Input Text    name=item_name    ${ITEM_NAME}
    Input Text    name=quantity    ${ITEM_QUANTITY}
    Input Text    name=value    ${ITEM_VALUE}
    Click Button    xpath=//button[text()='Add Item']
    Wait Until Page Contains    ${ITEM_NAME}

    # Step 3: Modify the Item (Selecting from Item List)
    Click Element    xpath=//tr[td[contains(., '${ITEM_NAME}')]]//a[contains(text(), 'Modify')]
    Input Text    name=item_name    ${UPDATED_NAME}
    Input Text    name=quantity    ${UPDATED_QUANTITY}
    Input Text    name=value    ${UPDATED_VALUE}
    Click Button    xpath=//button[text()='Update Item']
    Wait Until Page Contains    ${UPDATED_NAME}

    # Step 4: Delete the Item (Handling Confirmation Alert)
    Click Button    xpath=//tr[td[contains(., '${UPDATED_NAME}')]]//form//button[contains(text(), 'Delete')]
    Handle Alert    action=ACCEPT    # Accept the confirmation pop-up
    Wait Until Page Does Not Contain    ${UPDATED_NAME}

    # Step 5: Send Discord Notification
    Run Process    python    send_test_results.py    Item creation, modification, and deletion test completed successfully.

    # Step 6: Logout and Close Browser
    Close Browser