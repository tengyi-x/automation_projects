import re

from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

# all tests assumes user has signed in and installed the bugbug chrome extension

####################################################################
# CREATING PROJECT

# create_project(driver, project_name) creates a project using the driver driver, and project_name
def create_project(driver, project_name):
    # get and load webpage
    driver.get("https://app.bugbug.io/sign-in/")
    # time for user to login...
    time.sleep(15)
    # deleting popup option
    try:
        close_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='Modal.CloseButton']"))
        )
        close_button.click()
        print("Close button found")
    except TimeoutException:
        print("Error: 'Close' button cannot be found")
    # finding new project button
    try:
        project_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='ProjectList.NewProjectButton']"))
        )
        project_button.click()
        print("New project button found")
    except TimeoutException:
        print("Error: New project cannot be found")
    
    # Check if input fields for project name and homepage URL exist
    try:
        project_name_field = driver.find_element(By.XPATH, "//input[@placeholder='Example Airlines']")
        homepage_url_field = driver.find_element(By.XPATH, "//input[@placeholder='https://exampleairlines.com']")
        print("Input fields located")
    except NoSuchElementException:
        print("Error: Input fields for project name or homepage URL not found")
    
    # Checking project name should be entered
    try:
        # entering content in the homepage url field
        homepage_url_field.clear()
        homepage_url_field.send_keys("https://bugbug.io/v2/")
        # keeping the project name field empty
        project_name_field.clear()
        project_name_field.send_keys(Keys.ENTER)
        # attempting to locate message
        error_message_locator = (By.XPATH, "//div[contains(@class, 'sc-dSIIpw iILdZR') and contains(text(), 'This field is required')]")
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located(error_message_locator))
        # intended case: error message exists
        error_message = driver.find_element(*error_message_locator)
        if error_message.is_displayed():
            print("Project name field required")
            homepage_url_field.clear()
            project_name_field.clear()
        else:
            raise Exception("Error: Project name field not required")
    except TimeoutException:
        print("Error: Expected error message 'This field is required' did not appear for no project name")
    

    # enter project name and creating project
    try:
        # entering content in the homepage url field
        homepage_url_field.clear()
        homepage_url_field.send_keys("https://bugbug.io/v2/")
        # keeping the project name field empty
        project_name_field.clear()
        project_name_field.send_keys(project_name)
        project_name_field.send_keys(Keys.ENTER)
        # find "newtest" popup
        new_test_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//h3[@class='sc-dSCufp livljt' and contains(text(), 'New test')]"))
        )
        print("Project created")
        #close
        close_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='Modal.CloseButton']"))
        )
        close_button.click()
    except TimeoutException:
        print("Error: cannot create project")
    


 # Additional tests not mentioned may include: 
    #       "create project" button creates a new project
    #       "cancel" button does not save text fields
    #       x button on pop-up effectively closes window
    #       verify project is found on dashboard after exiting project_name
    #       project deletion and verifying deleted project not found on dashboard
    #       switching between projects

####################################################################
# TEST MANAGEMENT (creating, deleting, list, update)

# create_test(driver, test_name) creates a test and checks if it is present
# requires: project is open
def create_test(driver, test_name):
    try:
        # locate and click on the button to create a new test case
        create_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='TestsActions.CreateNewTest']"))
            )
        create_button.click()
        print("Create test button found")
    except NoSuchElementException:
        print("Error: Create test button not found")
    
    try:
        # enter the test case name through typing
        test_case_name_field = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//input[@data-testid='Input'][@name='name']"))
            )
        test_case_name_field.clear()
        test_case_name_field.send_keys(test_name)
        print("Test name entered")
    except NoSuchElementException:
        print("Error: Could not enter test name")
    
    try:
        # save the new test case
        test_case_name_field.send_keys(Keys.ENTER)
        # check testing environment is open
        test_record = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//p[contains(text(),'Create your first automated test by')]"))
            )
        print("Testing environment open")
    except TimeoutException:
        print("Error: Could not open testing envrionment")
    
    try:
        # exit test environment
        back_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Back']"))
            )
        back_button.click()
        print("Testing environment closed")
    except TimeoutException:
        print("Error: Could not close testing envrionment")
    
    try:
        # check test case is created
        time.sleep(2)
        test_in_list = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//span[@data-testid='TextCell'][1]"))
            )
        if test_in_list.text == test_name:
            print(f"Test case '{test_name}' created successfully!")
    except NoSuchElementException:
        print(f"Error creating test case '{test_name}'")

    # Additional tests not mentioned may include: 
    #       creating tests with the same names
    #       creating tests without names
    #       creating tests using the "create test" button
    #       "cancel" button does not save text fields
    #       x button on popup effectively closes window
    #       all the intended test functionalities exist on opened page
    #       created tests are in order
    #       number of tests is correct on top corner

# delete_test(driver, test_name) locates a test, opens it, deletes it, and checks if it is still present
# requires: project is open
def delete_test(driver, test_name):
    try:
        # locates tests in list
        test_list = WebDriverWait(driver, 10).until(
            EC.visibility_of_all_elements_located((By.XPATH, "//span[@data-testid='TextCell']"))
            )
        # iterate over tests to find one with test_name
        for test in test_list:
            # if the test matches test_name
            if test.text == test_name:
                time.sleep(2)
                new_button = test
                new_button.click()
                break
    except NoSuchElementException:
        print(f"Error: Could not find '{test_name}'")
    
    try:
        # finds three dot icon to delete test
        test_details = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='TestDetails.TestHeaderActions.Menu.Button']"))
            )
        test_details.click()
        time.sleep(1)
        # click delete in dropdown
        dropdown = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='TestDetails.TestHeaderActions.Menu.Items']"))
            )
        delete_button = dropdown.find_element(By.XPATH, ".//button[contains(text(), 'Delete')]")
        delete_button.click()
        # click delete in pop-up reminder
        delete_popup = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'sc-tagGq') and contains(., 'Delete test')]"))
            )
        delete_popup.click()
        print(f"{test_name} deleted in test environment")
    except NoSuchElementException:
        print(f"Error: Could not delete '{test_name}'")
    
    try:
        # locates tests in list
        time.sleep(2)
        test_list = WebDriverWait(driver, 10).until(
            EC.visibility_of_all_elements_located((By.XPATH, "//span[@data-testid='TextCell']"))
            )
        # iterate over tests to check test_name doesn't exist
        for test in test_list:
            # if the test matches test_name
            if test.text == test_name:
                raise Exception(f"Test with the name '{test_name}' still exists")
                
    except NoSuchElementException:
        print(f"Error: Could not find list of tests")

    # Additional tests not mentioned may include: 
    #       deleting multiple tests from the dashboard
    #       deleting all tests
    #       deleting tests with same names on different projects
    #       clicking "cancel" button after popup does not delete test
    #       x button on popup effectively closes window
    #       all other tests are unaffected
    #       number of tests is correct on top corner

# list_tests(driver, project) locates and outputes the list of tests created
# requires: project is open
def list_tests(driver):
    try:
        # wait for the tests list to be visible
        test_list = WebDriverWait(driver, 10).until(
            EC.visibility_of_all_elements_located((By.XPATH, "//span[@data-testid='TextCell']"))
        )
        # print test names
        for test in test_list:
            print(test.text)
        # take test names and store them in an array
        test_names = [test.text for test in test_list]
        return test_names
    except NoSuchElementException:
        print("Could not find tests")

# rename_test(driver, test_name, new_name) updates the test to a new name
# requires: project is open
def rename_test(driver, test_name, new_name):
    try:
        # locates tests in list
        test_list = WebDriverWait(driver, 10).until(
            EC.visibility_of_all_elements_located((By.XPATH, "//span[@data-testid='TextCell']"))
            )
        # iterate over tests to find one with test_name
        for test in test_list:
            # if the test matches test_name
            if test.text == test_name:
                time.sleep(2)
                new_button = test
                new_button.click()
                break
    except NoSuchElementException:
        print(f"Error: Could not find '{test_name}'")


    try:
        # finds three dot icon to delete test
        test_details = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='TestDetails.TestHeaderActions.Menu.Button']"))
            )
        test_details.click()
        time.sleep(1)
        # click rename in dropdown
        rename_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Rename']"))
        )
        rename_button.click()
        # locate the input field
        input_field = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[data-testid='Input']"))
        )
        # Check if the input field contains the test_name
        if input_field.get_attribute('value') == test_name:
            # Clear the input field
            input_field.clear()
            # Enter the new name
            input_field.send_keys(new_name)
            input_field.send_keys(Keys.ENTER)
            # check for success_message
            success_message = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//*[text()='Test has been updated successfully.']"))
        )
            print("Test renamed in test environment")
        else:
            raise Exception(f"Entered wrong test environment")
    except NoSuchElementException:
        print("An error occurred while renaming the test:")

    try:
        # exit test environment
        back_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Back']"))
            )
        back_button.click()
        print("Testing environment closed")
    except TimeoutException:
        print("Error: Could not close testing envrionment")
    
    try:
        # locates tests in list
        time.sleep(2)
        test_list = WebDriverWait(driver, 10).until(
            EC.visibility_of_all_elements_located((By.XPATH, "//span[@data-testid='TextCell']"))
            )
        # iterate over tests to check test_name doesn't exist
        for test in test_list:
            # if the test matches test_name
            if test.text == test_name:
                raise Exception(f"Test with the name '{test_name}' still exists")
        # iterate over tests to check new_name exists
        for test in test_list:
            # if the test matches test_name
            if test.text == new_name:
                print(f"{test_name} renamed to {new_name} successfully!")
    except NoSuchElementException:
        print(f"Error: Could not find list of tests")
    # Additional tests not mentioned may include: 
    #       renaming tests to same names
    #       duplicate test names present
    #       renaming through the project dashboard
    #       renaming through clicking on the test name
    #       other updates to test;
    #           screensize for test
    #           rerecord test
    #           change testing url

# Additional tests not mentioned may include:
#       other test functionalities:
#           duplicating tests
#           running tests
#           stopping testing in progress
#       searching for tests

####################################################################
# SUITES MANAGEMENT (creating, deleting, list, update) 
        
# create_suite(driver, suite_name) creates a testing suite with suite_name
# requires: project is open
def create_suite(driver, suite_name):
    try:
        # navigate to suites option from sidebar
        suites_navigate = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "svg[data-testid='SuitesIcon']"))
        )

        suites_navigate.click()
        print("Suites button clicked successfully!")
    except NoSuchElementException:
        print("Error: could not find Suites")
    
    try:
        # click on new_suite button
        new_suite_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='SuitesActions.CreateNewSuite']"))
        )
        new_suite_button.click()
        print("New suite button clicked successfully!")
    except NoSuchElementException:
        print("Error: could not find 'New Suite' button")
    
    try:
        # find the input field for name
        input_field = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='name']"))
        )
        # clear field
        input_field.clear()
        # check that it requires a name
        input_field.send_keys(Keys.ENTER)
        # wait for the error message
        error_message_locator = (By.XPATH, "//div[contains(@class, 'sc-dSIIpw iILdZR') and contains(text(), 'This field is required')]")
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located(error_message_locator))
        # check for the error message
        driver.find_element(*error_message_locator)
        print("Suite name required")
    except TimeoutException:
        print("Error: Expected error message 'This field is required' did not appear for no suite name")
    
    try:
        # input suite name
        input_field.send_keys(suite_name)
        input_field.send_keys(Keys.ENTER)
        # check for success message
        success_message = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//*[text()='Suite has been created successfully.']"))
        )
        print("Suite name added")
        # wait for the suite list to be visible
        suite_list = WebDriverWait(driver, 10).until(
            EC.visibility_of_all_elements_located((By.XPATH, "//span[@data-testid='TextCell']"))
        )
        # iterate to check newly created suite is present
        for suite in suite_list:
            if suite.text == suite_name:
                print(f"Suite {suite_name} created successfully!")
                break
    except NoSuchElementException:
        print("Error: Could not find created suite")
    
    # Additional tests not mentioned may include:
    #       customizing suite options with New Suite pop-up
    #           add tests, drag tests, search for tests
    #           auto-add, auto-retry, parallel cloud, profile
    #       checking for suite naming errors
    #       closing New Suite pop-up through either 'x' or 'Cancel' options

# delete_suite(driver, suite_name) deletes specified testing suite with suite_name
# requires: project is open
def delete_suite(driver, suite_name):
    try:
        suite_list = WebDriverWait(driver, 10).until(
            EC.visibility_of_all_elements_located((By.XPATH, "//span[@data-testid='TextCell']"))
        )
        # iterate to find suite_name
        for suite in suite_list:
            if suite.text == suite_name:
                    time.sleep(2)
                    print(f"{suite_name} found successfully!")
                    break
    except NoSuchElementException:
        print(f"Error: Could not find {suite_name} in list of Suites")
    
    try:
        # find the parent element (larger row)
        parent_suite = suite.find_element(By.XPATH, "./ancestor::a")
        # hover over the parent element
        ActionChains(driver).move_to_element(parent_suite).perform()
        # then find the suite-specific dropdown button
        dropdown_button = WebDriverWait(parent_suite, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='Dropdown.IconButton']"))
            )
        time.sleep(2)
        dropdown_button.click()
        # navigate to delete button in dropdown menu
        delete_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Delete']"))
        )
        time.sleep(2)
        delete_button.click()
        print("Delete button clicked in dropdown menu")
        # press confirmation "Yes" button in pop-up
        confirm_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='ConfirmModal.ConfirmButton']"))
            )
        time.sleep(2)
        confirm_button.click()
        print("Delete confimation button clicked in pop-up")
    except TimeoutException:
        print(f"Error: Could not find delete options")
    
    try:
        # checking for success message
        success_message = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//*[text()='Suites have been deleted successfully.']"))
        )
    except NoSuchElementException:
        print("Error: No success message")
    
    try:
        # check for suite_name in list
        suite_list = WebDriverWait(driver, 10).until(
            EC.visibility_of_all_elements_located((By.XPATH, "//span[@data-testid='TextCell']"))
        )
        # iterate to find suite_name
        for suite in suite_list:
            if suite.text == suite_name:
                raise Exception(f"{suite_name} still exists in list")
            
        print(f"{suite_name} deleted successfully!")
    except Exception as e:
        print("Error:", e)

    # Additional tests not mentioned may include:
    #       deleting multiple suites at once
    #       deleting all suites
    #       ensuring suite deletion does not affect tests
    #       deleting certain tests from a suite
    #       closing pop-up through either 'x' or 'No' options

# list_Suites(driver) locates and outputs the list of suites created
# requires: project is open
def list_suites(driver):
    try:
        suite_list = WebDriverWait(driver, 10).until(
            EC.visibility_of_all_elements_located((By.XPATH, "//span[@data-testid='TextCell']"))
        )
        # initialize suite_names
        suite_names = [];
        # iterate to print suites
        for suite in suite_list:
            # textcells also take in 0 (number of tests)
            if suite.text != "0" and suite.text != "All tests":
                print(suite.text)
                # take suite names and store them in an array
                suite_names.append(suite.text)
        return suite_names
    except NoSuchElementException:
        print(f"Error: Could not find list of suites")

# rename_suite(driver, suite_name, new_name) updates suite name to a new name
# requires: project is open
def rename_suite(driver, suite_name, new_name):
    try:
        suite_list = WebDriverWait(driver, 10).until(
            EC.visibility_of_all_elements_located((By.XPATH, "//span[@data-testid='TextCell']"))
        )
        # iterate to find suite_name
        for suite in suite_list:
            if suite.text == suite_name:
                    time.sleep(2)
                    print(f"{suite_name} found successfully!")
                    break
    except NoSuchElementException:
        print(f"Error: Could not find {suite_name} in list of Suites")
    
    try:
        # find the parent element (larger row)
        parent_suite = suite.find_element(By.XPATH, "./ancestor::a")
        # hover over the parent element
        ActionChains(driver).move_to_element(parent_suite).perform()
        # then find the suite-specific dropdown button
        dropdown_button = WebDriverWait(parent_suite, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='Dropdown.IconButton']"))
            )
        time.sleep(2)
        dropdown_button.click()
        # navigate to rename button in dropdown menu
        delete_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Rename']"))
        )
        time.sleep(2)
        delete_button.click()
        print("Rename button clicked in dropdown menu")
    except NoSuchElementException:
        print(f"Error: Could not find rename options")

    try:
        # since text is already highlighted, typing in directly functions
        actions = ActionChains(driver)
        actions.send_keys(new_name)
        actions.send_keys(Keys.RETURN)
        actions.perform()
    except TimeoutError:
        print(f"Error: Could not enter new name")
    
    try:
        # check for success message
            success_message = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//*[text()='Suite has been updated successfully.']"))
        )
            print("Suite renamed in suite environment")
    except NoSuchElementException:
        print("An error occurred while renaming the test:")
    
    try:
        time.sleep(2)
        suite_list = WebDriverWait(driver, 10).until(
            EC.visibility_of_all_elements_located((By.XPATH, "//span[@data-testid='TextCell']"))
        )
        # iterate over suite list to check suite_name doesn't exist
        for suite in suite_list:
            if suite.text == suite_name:
                raise Exception(f"Suite with the name '{suite_name}' still exists")
        # iterate over suite list to check new_name exists
        for suite in suite_list:
            if suite.text == new_name:
                print(f"{suite_name} renamed to {new_name} successfully!")
                break
    except NoSuchElementException:
        print(f"Error: Could not find list of suites")

    # Additional tests not mentioned may include: 
    #       renaming suites to same names
    #       duplicating suites
    #       renaming through opening suite pop-up
    #       other updates to test;
    #           adding tests
    #           editing tests
    #           dragging tests
    #           deleting tests
    #           reordering tests

# Additional tests not mentioned may include:
#       running a testing suite
#       searching for suites
#       checking number of tests display
#       verifying last result display
    

####################################################################
# HOW TO RUN TEST CASES
# the functions above verify the manipulations of the website
# act as they should, but they should also be stacked like so to 
def testing_tests_example():
    # initialize driver
    driver = webdriver.Chrome()
    create_project(driver, "project1")
    # creating three tests and checking the list
    create_test(driver, "test4")
    create_test(driver, "test2")
    create_test(driver, "test9")
    output = list_tests(driver)
    expected_test_list = ["test9", "test2", "test4"]
    assert(output == expected_test_list)
    # renaming test9 to test0, and checking the list
    rename_test(driver, "test9", "test0")
    output = list_tests(driver)
    expected_test_list = ["test0", "test2", "test4"]
    assert(output == expected_test_list)
    # deleting test2 and checking the list
    delete_test(driver, "test2")
    output = list_tests(driver)
    expected_test_list = ["test0", "test4"]
    assert(output == expected_test_list)
    print("TEST END")

def testing_suites_example():
    # initialize driver
    driver = webdriver.Chrome()
    create_project(driver, "project2")
    # creating notme suites and checking the list
    create_suite(driver, "notme")
    create_suite(driver, "suite1")
    create_suite(driver, "nope")
    time.sleep(5)                   # slowing it down because success popups build up quickly
    output = list_suites(driver)
    print(output)
    expected_test_list = ["notme", "suite1", "nope"]
    assert(output == expected_test_list)
    # deleting suite1 and checking the list
    delete_suite(driver, "suite1")
    output = list_suites(driver)
    expected_test_list = ["notme", "nope"]
    assert(output == expected_test_list)
    # creating byebye and checking the list
    create_suite(driver, "byebye")
    output = list_suites(driver)
    expected_test_list = ["notme", "nope", "byebye"]
    assert(output == expected_test_list)
    time.sleep(2)
    # renaming byebye to hello and checking the list
    rename_suite(driver, "byebye", "hello")
    output = list_suites(driver)
    expected_test_list = ["notme", "nope", "hello"]
    assert(output == expected_test_list)
    print("TEST END")


# running tests on suites:
testing_suites_example()