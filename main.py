from bs4 import BeautifulSoup
import os
import requests

def create_link(url, sub_id):
    partition = url.split('/')
    partition.pop()
    partition[partition.index('problem')] = 'submission'
    url = '/'.join(partition)
    return 'https://codeforces.com' + url + '/' + sub_id

def get_id(user):
    try:
        response = requests.get('https://codeforces.com/submissions/' + user).text
        soup = BeautifulSoup(response, 'lxml')
        id = soup.find('table', class_ = 'status-frame-datatable')
        id = id.find_all('tr')
        for i in id:
            #print(i.get('partymemberids'))
            if i.get('partymemberids') != None:
                return i.get('partymemberids')
    except:
        return get_id(user)


def get_all_links(user, page):
    url = 'https://codeforces.com/submissions/' + user + '/page/' + str(page)

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        problem_links = soup.find_all('tr', partymemberids=get_id(user))

        links = []
        for problem_link in problem_links:
            link = problem_link.find_all('td', class_ = "status-small")
            submission_id = problem_link['data-submission-id'].strip()
            judge_status = problem_link.find('span', class_ = 'verdict-accepted')
            if judge_status == None:
                continue
            main_link = ''
            name = ''
            for problem in link:
                tmp_link = problem.find('a')
                if tmp_link != None:
                    name = tmp_link.text.strip()
                    main_link = tmp_link['href'].strip()
                    break

            links.append((name, create_link(main_link, submission_id)))
        return links
    except:
        return get_all_links(user, page)

def get_source_code(link):
    try:
        response = requests.get(link).text
        soup = BeautifulSoup(response, 'lxml')
        source = soup.find('pre', id='program-source-text')
        return source.text
    except:
        return None

def count_maximum_page(user):
    try:
        url = 'https://codeforces.com/submissions/' + user
        response = requests.get(url).text
        soup = BeautifulSoup(response, 'lxml')
        pages = soup.find_all('span', class_ = 'page-index')

        total = 0
        for page in pages:
            total = max(total, int(page.a.text))
        return total
    except:
        return count_maximum_page(user)

def main():
    username = input('Codeforces handle:')
    pages = count_maximum_page(username)

    print(username + "\'s", 'total submission pages are', pages)
    print(f'Download page range i.e. 1 to {pages}:')
    start, end = [int(x) for x in input().split(' ')]

    if min(start, end) < 1 or max(start, end) > pages or start > end:
        raise Exception('invalid range')

    path = input('Directory:')
    path += '/' + username

    print('Working on codeforces...')

    try:
        os.mkdir(path)
    except:
        pass

    names = {}
    for page in range(start, end + 1):
        print('We are at page', page)
        links = get_all_links(username, page)

        for (name, link) in links:
            print('Downloading', name)
            # print(link)
            source = get_source_code(link)
            if source == None:
                print('Downloading can\'t be performed for', name)
                continue
            filename = name
            if name in names.keys():
                names[name] += 1
                filename += str(names[name])
            else:
                names[name] = 1
            filename += '.txt'

            try:
                file = open(path + '/' + filename, 'w')
                file.write(source)
                file.close()
            except:
                print('Downloading ignored for', name)
                print('Directory or username may be wrong')


if __name__ == '__main__':
    main()


