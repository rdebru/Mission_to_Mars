
# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import datetime as dt
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager


def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)
    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres": hemisphere_urls(browser)
    }
    # Stop web driver and return data
    browser.quit()
    return data


def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        slide_elem.find('div', class_='content_title')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


# ### JPL Space Images Featured Images
def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')
    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    except AttributeError:
        return None

        # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url


# ## Mars Facts
def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()


# # D1: Scrape High-Resolution Mars’ Hemisphere Images and Titles
# ### Hemispheres
def hemisphere_urls(browser):
    # 1. Use browser to visit the URL
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    # image_links = browser.find_by_tag("h3").links.find_by_partial_text("Hemisphere")

    # Loop through the full-resolution image URL
    for i in range(4):
        # Create an empty dictionary to url and title
        hemispheres = {}

        browser.find_by_css('a.product-item h3')[i].click()

        # HTML object
        html = browser.html
        # Parse the resulting html with soup
        img_soup = soup(html, 'html.parser')

        # Add try/except for error handling
        try:
            # retrieve the full-resolution image string
            sample_img = img_soup.find('a', text='Sample')["href"]

            # Use the base url to create an full Img url
            img_url2 = f'https://marshemispheres.com/{sample_img}'

            #  the full resolution image URL as value for img_url key
            hemispheres['img_url'] = img_url2

            #  image title as the value for the title key
            hemispheres['title'] = img_soup.find('h2', class_="title").text

        except AttributeError:
            return None

        # add the dictionary to the list
        hemisphere_image_urls.append(hemispheres)

        # navigate back to the beginning to get the next hemisphere image.
        browser.back()

    # 4. Print the list that holds the dictionary of each image url and title.
    return hemisphere_image_urls

    # 5. Quit the browser
    # browser.quit()


if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())
