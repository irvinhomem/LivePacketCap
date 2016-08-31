import random
import logging
import linecache

# Configure Logging
logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
#self.logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)
#self.logger.setLevel(logging.WARNING)

text_file = 'Alice-in-Wonderland-Carroll.txt'

def read_single_random_line():
    lines = random.choice(open(text_file, 'r').readlines())
    logger.debug('Lines:')
    logger.debug('**: %s' % lines)

def get_paragraph_line_number_starts(txt_f):
    paragraph_starts = []
    my_file = open(txt_f, 'r')
    for count, line in enumerate(my_file):
        # logger.debug('COUNT: %i' % count)
        # logger.debug('**LINE 1: %s' % line)

        # try:
        line1 = linecache.getline(text_file, count + 1)
        #logger.debug('Line: %s' % str(line1))
        line2 = linecache.getline(text_file, count + 2)
        #logger.debug('Line: %s' % str(line2))
        line3 = linecache.getline(text_file, count + 3)
        #logger.debug('Line: %s' % str(line3))

        if line1.endswith('\n') and line2.startswith('\n'):
            if not line3.startswith('\n'):
                paragraph_starts.append(count+3)
                #logger.debug('COUNT +3 (Line number [1-start]): %s' % str(count+3))
                logger.debug('Para start: %s' % str(linecache.getline(text_file, count+3)))
        # except:
        #     logger.debug('EOL or some other error')

    # logger.debug('Paragraph starts list length: %i' % len(paragraph_starts))
    # logger.debug('Paragraph 1 line num: %i' % paragraph_starts[0])
    # logger.debug('Paragraph 2 line num: %i' % paragraph_starts[1])
    # logger.debug('Paragraph 3 line num: %i' % paragraph_starts[2])
    # logger.debug('Paragraph 10 line num: %i' % paragraph_starts[9])

    return paragraph_starts

def pick_random_paragraph(para_starts_list):
    selected_para_line_num = random.choice(para_starts_list)
    logger.debug('Selected Paragraph Number: %s' % selected_para_line_num)

    para_index = para_starts_list.index(selected_para_line_num)
    logger.debug('Paragraph index: %i' % para_index)
    next_para_num = para_starts_list[para_index+1]

    logger.debug('LINE %i: %s' % (selected_para_line_num, str(linecache.getline(text_file, selected_para_line_num))))

    my_paragraph = ''
    for count in range(selected_para_line_num, next_para_num):
        my_paragraph.join(linecache.getline(text_file,count))

    logger.debug('Paragraph:')
    logger.debug('--> %s' % my_paragraph)


para_num_list = get_paragraph_line_number_starts(text_file)
pick_random_paragraph(para_num_list)
