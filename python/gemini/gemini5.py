#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
from datetime import datetime

import frontmatter
from slugify import slugify

from util import par_dir, mkdir_p
from leetcode import Leetcode
from lintcode import Lintcode
from summary import update_summary
from ojhtml2markdown import problem2md

BASEDIR = os.path.abspath(os.path.dirname(__file__))


def _get_current_time_string():
    """Returns the current time as a formatted string."""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Helper for GitBook algorithm')
    parser.add_argument('--new', type=str, dest='new',
                        help='Create a new post with given leetcode/lintcode URL.')
    parser.add_argument('--dir', type=str, dest='dir',
                        help='Create markdown file under the specified directory.')
    parser.add_argument('--update', nargs='*', dest='update',
                        help='Update post with given title in post and summary.')
    parser.add_argument('--migrate', type=str, dest='migrate',
                        help='Migrate old posts.')
    parser.add_argument('--fix-summary', dest='fix_summary',
                        help='Render a new summary from posts.')
    args = parser.parse_args()
    print('Called with arguments: {}'.format(args))

    ROOTDIR = par_dir(BASEDIR)

    if args.new:
        raw_url = args.new
        problem_md = ''
        problem_slug = ''
        online_judge = None
        convert_description = True

        if raw_url.startswith('https://leetcode'):
            online_judge = Leetcode()
        elif raw_url.startswith('https://www.lintcode.com'):
            online_judge = Lintcode()
            convert_description = False

        problem = online_judge.get_problem_all(raw_url)
        problem_slug = slugify(problem['title'], separator="_")
        problem_md = problem2md(problem, convert_description)

    if args.dir:
        post_dir = os.path.join(ROOTDIR, args.dir)
        post_filename = os.path.join(post_dir, problem_slug + '.md')
        summary_relative_path = args.dir.strip('/').split('/')[-1] + '/' + problem_slug + '.md'
        summary_line = '* [{title}]({path})'.format(title=problem['title'], path=summary_relative_path)
        print(summary_line)
        mkdir_p(post_dir)
        with open(post_filename, 'w', encoding='utf-8') as file:
            print('Creating post file {}...'.format(post_filename))
            file.write(problem_md)

    if args.fix_summary:
        update_summary(ROOTDIR)