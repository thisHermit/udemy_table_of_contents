from selenium import webdriver
import time
import re
import click


@click.group()
def cli():
    """Get the table of contents from a Udemy course site"""
    pass


def get_table_of_contents(url: str) -> str:
    #  TODO: add bot protection fails
    driver = webdriver.Chrome()
    driver.get(url)

    time.sleep(0.5)
    table_of_contents = driver.find_element_by_class_name(
        "ud-component--clp--curriculum")

    # click on  sections button
    time.sleep(2)
    table_of_contents.find_element_by_class_name("sections-toggle").click()

    #  FIXME: not all lectures are returned in the table of contents
    return table_of_contents.text


def print_lectures(lectures) -> str:
    string = ""
    flag = 0
    for lecture in lectures:
        # check if the line shows the duration of the lecture
        # or just shows the preview of the lecture
        if re.search('^[^0-9].*',
                     lecture) and not lecture.startswith('Preview'):
            if flag == 0:
                # first line would be a module
                # so use a h1 for better syntax
                string += "## {}".format(lecture)
                flag = 1
            else:
                string += "* {}".format(lecture)
            string += "\n"
    return string


@cli.command()
@click.option('--online',
              is_flag=True,
              default=True,
              help='get the website online')
@click.argument('url', default='urls.txt', type=click.STRING)
def toc(url, online):
    if url.endswith(".txt"):
        # Loop
        with open(url, 'r') as f:
            urls = f.readlines()
        for link in urls:
            write_toc_file(link, online)
    else:
        # goto url and then read the toc
        write_toc_file(url, online)


def write_toc_file(url, online):
    # url = "https://www.udemy.com/course/understanding-typescript/"
    table_of_contents = ""
    course_name = url.split('/')[-2]
    if online:
        # get the data from the website first
        table_of_contents = get_table_of_contents(url)

        with open('toc_{}.txt'.format(course_name), 'w') as f:
            f.write(table_of_contents)
    else:
        # get the data from the file if stored
        with open('toc_{}.txt'.format(course_name), 'r') as f:
            table_of_contents = ''.join(f.readlines())

    outfile = ""
    modules = table_of_contents.split('\n+')
    for module_index, module in enumerate(modules):
        # print the lectures in each module
        lectures = None
        if module_index:
            # Normal Use
            lectures = module.split('\n')
        else:
            # First Module (due to '-' sign this step is separate)
            lectures = module.split('–')[-1].split('\n')[1:]

        outfile += print_lectures(lectures)

    with open('toc_{}.md'.format(course_name), 'w') as f:
        f.write("# {}\n".format(course_name.capitalize().replace('-', ' ')))
        f.write(outfile)


if __name__ == "__main__":
    cli()
