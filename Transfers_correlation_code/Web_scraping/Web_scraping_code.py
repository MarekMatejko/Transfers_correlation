import pandas as pd
import time
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup


# Initialize WebDriver
def initialize_driver(url):
    driver = webdriver.Chrome()
    driver.get(url)
    driver.implicitly_wait(5)
    return driver


# Adjust zoom leve, becuse selenium need see all the webpage
def adjust_zoom(driver, zoom_out_times=6):
    for _ in range(zoom_out_times):
        pyautogui.hotkey('ctrl', 'subtract')


# Get season data
def getting_new_webpage(driver, season_text, next_season_text):
    time.sleep(1)
    element = driver.find_element(By.XPATH, f'//span[text()="{season_text}"]')
    ActionChains(driver).click(element).send_keys(next_season_text).perform()
    ActionChains(driver).send_keys(Keys.ENTER).perform()

    # Check if a second interaction is necessary, becuse in transfer webpage we have season from "" until ""
    try:
        element = driver.find_element(By.XPATH, f'//span[text()="{season_text}"]')
        ActionChains(driver).click(element).send_keys(next_season_text).perform()
        ActionChains(driver).send_keys(Keys.ENTER).perform()
    except:
        print(f"No second interaction required for season {season_text}.")

    # In webpage with season statistics we have "Show" button
    try:
        button = driver.find_element(By.CSS_SELECTOR, 'input[type="submit"].button.small[value="Show"]')
        button.click()
        print(f"Clicked 'Show' for season {next_season_text}.")
    # In webpage with transfer season we have "Display selection" button
    except:
        try:
            button = driver.find_element(By.CSS_SELECTOR,
                                         'input[type="submit"].button.small[value="Display selection"]')
            button.click()
            print(f"Clicked 'Display selection' for season {next_season_text}.")
        except Exception as e:
            print(f"Failed to click button for season {next_season_text}: {e}")

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', class_="items").tbody
    trs = table.find_all('tr')

    return trs


# Getting season data
def getting_season_data(trs, next_season_text):
    teams, places, matches, wins, draws, loses, goals, goals_diff, points = ([] for _ in range(9))

    for tr in trs:
        team_element = tr.find('td', class_="no-border-links hauptlink")
        place_element = tr.find('td', class_="rechts hauptlink")

        if team_element and place_element:
            teams.append(team_element.text)
            places.append(place_element.text)
            tds = tr.find_all('td', class_="zentriert")
            matches.append(tds[1].text.strip() if len(tds) > 1 else '')
            wins.append(tds[2].text.strip() if len(tds) > 2 else '')
            draws.append(tds[3].text.strip() if len(tds) > 3 else '')
            loses.append(tds[4].text.strip() if len(tds) > 4 else '')
            goals.append(tds[5].text.strip() if len(tds) > 5 else '')
            goals_diff.append(tds[6].text.strip() if len(tds) > 6 else '')
            points.append(tds[7].text.strip() if len(tds) > 7 else '')
        else:
            print(f"Missing data for one of the elements in row: {tr}")

    return pd.DataFrame({
        'Teams': teams,
        'Places': places,
        'Matches': matches,
        'Wins': wins,
        'Draws': draws,
        'Loses': loses,
        'Goals': goals,
        'Goals Diff': goals_diff,
        'Points': points,
        'Year': next_season_text
    })


# Getting season data for transfers
def getting_transfers_data(trs, next_season_text):
    teams, spends, balances = [], [], []

    for tr in trs:
        team_element = tr.find('td', class_="hauptlink no-border-links")
        spend_element = tr.find('td', class_="rechts hauptlink redtext")
        balance_element = tr.find('td', class_="rechts hauptlink")

        if team_element and spend_element and balance_element:
            teams.append(team_element.text)
            spends.append(spend_element.text)
            balances.append(balance_element.text)
        else:
            print(f"Missing data for one of the elements in row: {tr}")

    return pd.DataFrame({
        'Teams': teams,
        'Spend': spends,
        'Balance': balances,
        'Year': next_season_text
    })


def main_getting_scraping_data(url, parse_function):
    driver = initialize_driver(url)
    adjust_zoom(driver)

    start_season, end_season = 24, 5
    df_seasons_statistics = pd.DataFrame()

    for year in range(start_season, end_season - 1, -1):
        season_text = f"{str(year).zfill(2)}/{str(year + 1).zfill(2)}"
        next_season_text = f"{str(year - 1).zfill(2)}/{str(year).zfill(2)}"
        trs = getting_new_webpage(driver, season_text, next_season_text)
        df_season = parse_function(trs, next_season_text)
        df_seasons_statistics = pd.concat([df_seasons_statistics, df_season], ignore_index=True)

    driver.quit()
    return df_seasons_statistics