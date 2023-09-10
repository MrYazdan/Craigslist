import sys
import json

from tqdm import tqdm
from time import sleep
from uuid import uuid4
from loguru import logger
from datetime import datetime
from InquirerPy import prompt
from config import variables, selectors
from config.handlers import NotifyHandler
from core.utils import get_browser, querySelector,  querySelectorAll, removeElement, click

# configure logging:
logger.remove()
logger.add(NotifyHandler(), format="{message}", level="SUCCESS")
logger.add(sys.stdout, format="[{time:HH:mm:ss}] <lvl>{message}</lvl>", level="INFO")

# start the crawler:
if __name__ == '__main__':
    questions = [
        {
            "type": "list",
            "message": "🙋🏻‍ Hi there, welcome to Craigslist crawler\n"
                       "From which city would you like to receive the latest announcements?",
            "choices": variables.city_links.keys(),
        },
        {"type": "confirm", "message": "Confirm ?"},
    ]
    cli = prompt(questions)
    if not cli[1]:
        logger.error("Good luck next time!  👋🏻")
        exit()

    # get browser instance:
    base_url = variables.city_links[cli[0]]
    logger.success(f"Starting crawler from {base_url} ✅")
    browser = get_browser(base_url)

    # navigate to the page with housing ads:
    logger.info("Navigate to the page with housing ads")
    browser.get(browser.current_url + variables.housing_args)

    # calculate the number of pages:
    logger.info("Calculate the number of pages")
    main_url = browser.current_url

    if (no_ads_button := querySelector(selectors.no_ads_button, browser)) and no_ads_button.is_displayed():
        logger.error("🤕 There are no ads on this page, exiting...\nGood luck next time 👋🏻")
        exit()

    btn = querySelector(selectors.last_page_button, browser)
    if btn.get_attribute('disabled'):
        page_counts = 1
    else:
        click(btn, browser)
        sleep(2)
        page_counts = int(querySelectorAll(selectors.page_counts, browser)[-1].text.replace(",", "").split(" of ")[-1])
        page_counts = page_counts // 120 + 1

        browser.get(main_url)

    # get the number of pages:
    if int(page_counts) > 1:
        cli = prompt([
            {
                "type": "input",
                "name": "pages",
                "message": f"How many pages would you like to crawl? (each page contains 120 ads) [1 - {page_counts}]",
                "validate": lambda x: (x.isdigit() and (0 < int(x) <= int(page_counts))),
                "invalid_message": f"Please enter a valid number between 1 to {page_counts}"
            }
        ])
    else:
        cli = {"pages": "1"}

    pages = int(cli["pages"])
    logger.info(f"🦎 Crawling {pages} pages ...")

    ads_list = []
    ads_len = 0
    _try = 3

    while ads_len == 0 and _try != 0:
        try:
            for page_number in range(pages):
                browser.get(variables.page_link(base_url, page_number))
                logger.info(f"🔎 Crawling ads on page {page_number + 1}")

                # get the ads:
                for el in querySelectorAll(selectors.ads_list, browser):
                    ads_list.append({
                        "title": querySelector(selectors.ads_title, el).text,
                        "link": querySelector(selectors.ads_a_tag, el).get_attribute("href"),
                    })
            ads_len = len(ads_list)
        except Exception as e:
            logger.error(f"⚠：Retrying in 3 seconds...")
            sleep(_try)
            _try -= 1

    logger.success(f"✅ Crawling step 1 finished! ▶ （{len(ads_list)} ads found）")

    # ask for the counts of ads to scrape:
    cli = prompt([{
        "message": f"How many ads would you like to scrape? [1 - {ads_len}]",
        "type": "input",
        "name": "count",
        "validate": lambda x: (x.isdigit() and (0 < int(x) <= int(ads_len))),
        "invalid_message": f"Please enter a valid number between 1 to {ads_len}"
    }])

    ads_count = int(cli["count"])

    data_list = []
    # get the ads:
    for ad_item, step_tqdm in zip(enumerate(ads_list[:ads_count]), tqdm(range(ads_count-1))):
        ind, ad = ad_item

        try:
            data = {}
            browser.get(ad["link"])

            # normalize document:
            removeElement(querySelector('.show-contact', browser), browser)
            removeElement(querySelector('#postingbody > div', browser), browser)
            removeElement(querySelector('#display-date', browser), browser)

            # get normal datetime from posted and updated field:
            if times := querySelectorAll(selectors.ad_datetime_field, browser):
                click(times[0], browser)

            data["link"] = browser.current_url
            data["id"] = tmp.split(".")[0] if '.' in (tmp := browser.current_url.split("/")[-1]) else None
            data["price"] = tmp.text if (tmp := querySelector(selectors.ad_price, browser)) else None
            data["status"] = tmp.text if (tmp := querySelector(selectors.ad_status, browser)) else None
            data["title"] = tmp.text if (tmp := querySelector(selectors.ad_title, browser)) else None
            data["description"] = tmp.text if (tmp := querySelector(selectors.ad_description, browser)) else None
            data["volume"] = (tmp.text[2:] if len(tmp.text) > 3 else tmp) \
                if (tmp := querySelector(selectors.ad_volume, browser)) else None

            if times:
                if len(times) >= 2:
                    data["posted_at"] = times[0].text
                    data["updated_at"] = times[1].text
                elif len(times) == 1:
                    data["posted_at"] = times[0].text
                    data["updated_at"] = None
                else:
                    data["posted_at"] = None
                    data["updated_at"] = None

            data["images"] = \
                [a.get_attribute("href") for a in querySelectorAll(selectors.ad_images, browser)]

            attrs = []
            if (attr_groups := querySelectorAll(selectors.ad_attr_groups, browser)) and len(attr_groups) > 1:
                _ = [querySelectorAll('span', attr_group) for attr_group in attr_groups[1:]]
                attrs = [item.text for sublist in _ for item in sublist]

            data['attributes'] = attrs
            data_list.append(data)

            # logger.success(f"✅ Scrapped {ind + 1} of {ads_count} ads ✅")
        except Exception as e:
            logger.error(f"Error occurred while scrapping data from this ad ({ad['link']}):\n{e}")

    # save the data into json file:
    logger.info("Saving data into json file")
    filename = '{:%Y-%m-%d_%H-%M-%S}_{}'.format(datetime.now(), uuid4().clock_seq)

    with open(f"{filename}.json", "w") as json_file:
        json.dump(data_list, json_file, indent=4, ensure_ascii=False)

    # finish the process:
    logger.success(f"✅ Crawling step 2 finished! ▶ （{len(ads_list)} ads saved to json file）")
    logger.opt(colors=True).info(f"🔗 Path: <l><m><i>{filename}.json</i></m></l>")
    logger.opt(colors=True).info(f"<w><C>- Good luck! -</C></w>")

    browser.close()
    exit()
