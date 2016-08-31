import random
import logging

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
        logger.debug('COUNT: %i' % count)
        logger.debug('LINE: %s' % line)
        try:
            line2 = my_file.readline()
            logger.debug('**Line 1: %s' % line2)
            line3 = my_file.readline()
            logger.debug('**Line 2: %s' % line3)


            # if line.endswith('\n') and my_file.readline(count+1).startswith('\n'):
            #     if not my_file.readline(count+2).startswith('\n'):
            #         paragraph_starts.append(count+2)
            #         logger.debug('COUNT +2: %s' % str(count+2))
            #         logger.debug('Para start: %s' % str(my_file.readline()))
        except:
            logger.debug('EOL or some other error')

    logger.debug('Paragraph starts list length: %i' % len(paragraph_starts))
    logger.debug('Paragraph 1 line num: %i' % paragraph_starts[0])
    logger.debug('Paragraph 2 line num: %i' % paragraph_starts[1])
    logger.debug('Paragraph 3 line num: %i' % paragraph_starts[2])
    logger.debug('Paragraph 10 line num: %i' % paragraph_starts[9])




get_paragraph_line_number_starts(text_file)
