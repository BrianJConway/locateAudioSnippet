#! python3
# Downloads every single MBMAM episode.
import requests
import os
import bs4

# Create folder to store podcasts
os.makedirs('mbmbam', exist_ok=True)
os.chdir('/media/linux/Flash')

# Base URL
baseUrl = 'http://mbmbam.libsyn.com/webpage'

# Set initial month and year
month = 6
year = 2012

# Set ending month and year
endMonth = 9
endYear = 2017

# Set current url
currentUrl = baseUrl + '/' + str(year) + '/' + str(month)

# Loop through all years of available podcasts
while not (year == endYear and month == endMonth):
    # Download the current page.
    print('Downloading page %s...' % currentUrl)
    res = requests.get(currentUrl)
    res.raise_for_status()

    # Create the soup object from the page's html
    soup = bs4.BeautifulSoup(res.text, "lxml")

    # Find the URLs of the download links.
    podcastLinks = soup.select('.postDetails a')

    # Check if no podcasts found
    if podcastLinks == []:
        print('Could not find any podcast episodes')
    # Otherwise, assume podcast found
    else:
        # Loop through each found link
        for currentLink in podcastLinks:
            # Get the URL
            url = currentLink.get('href')
            
            # Ensure link is for a podcast episode
            if url.startswith('http://'):
                # Set filename for current episode
                fileName = currentLink.get_text()

                print('Downloading . . . ' + url)

                # Download episode content
                res = requests.get(url)
                res.raise_for_status()

                # Create file for current episode
                podcastFile = open(os.path.join('mbmbam', fileName), 'wb')

                # Write episode content to the file
                for chunk in res.iter_content(100000):
                    podcastFile.write(chunk)
                podcastFile.close()
                
                print('Done.')

    # Increment month, and year if necessary
    month += 1
    if month == 13:
        month = 1
        year += 1

    # Set next url
    currentUrl = baseUrl + '/' + str(year) + '/' + str(month)

print('All Done.')
