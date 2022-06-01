# Changing-Room-Coding-Challenge

### Table of Contents

- [Web Scraper](#web-scraper)
- [Automatic Update](#automatic-update)
- [Data Storage](#data-storage)


---

## Web Scraper

I write an application to crawl the offical website of the [Reformation](https://www.thereformation.com/clothing).

There are several things I would to mention:

1. I only set the number of scrolls to be 1 for demostration. In real application, this number can be set larger or we can employ the method that I comment out to __scroll down to the end__. Also, we can allow for __more wait time between each scroll__ so that we can __scrape the whole website and extract all the URLs__.

2. On the product page, the brand sometimes does not introduce the product material. To accommodate this issue, I always include washing instructions since they also indicate the product material.

3. It is very likely that one product has different colors. However, since you require the color to be str, I only scrape the default color on the display page.

4. I only include the available size of the selected color.

5. Since Reformation only sells women's clothes and new clothes, the gender will always be women and the secondhand will always be False.

6. For better presentation, I added two print statements to show the total number of clothes and the progress of getting info of the clothes.

---

## Automatic Update
I schedule the Python script as Cron Jobs with the build-in function Crontab on Mac.

I first write the command ```crontab -e``` to the terminal and press ```i``` to enter the ```INESRT``` mode.

With the help of [Crontab Guru](https://crontab.guru/#0_0_*_*_*), I easily determine the entries that can let the database update at 00:00 every day.

The command is ```0 0 * * *    ~/miniforge3_new/bin/python /Users/sihanzhang/Desktop/Changing_Room/web-crawler.py```

Next, I press ```escape``` to quit the ```INESRT``` mode and type ```:wq``` to quit the editor.

Then, I enter the command ```crontab -l``` to check whether the cron job is set.

Note that to use the crontab, we must grant Full Disk Access to cron with [instructions](https://www.bejarano.io/fixing-cron-jobs-in-mojave/)

I use logger to record the update times. The specific update times will be tracked in the log file. Note that the log file will also record if we run the Python script manually.


---

## Data Storage

I create a Postgres database on AWS and store the data as a table called ```reformation``` in it. 

Then, I use Postgres.sql and pgAdmin to check that the reformation table is now stored successfully in the database.

Since I am afraid that if I let the instance running, the usage will go beyond the free tier usage, I stopped the instance.