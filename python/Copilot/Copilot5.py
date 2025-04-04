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

def curr_time():
    """
    Returns the current time formatted as a string.
    """
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def main():
    parser = argparse.ArgumentParser(description='Helper for GitBook algorithm')
    parser.add_argument('--new', type=str, dest='new', help='Create new post with given leetcode/lintcode URL.')
    parser.add_argument('--dir', type=str, dest='dir', help='Create markdown under specified directory.')
    parser.add_argument('--update', nargs='*', dest='update', help='Update post with given title in post and summary.')
    parser.add_argument('--migrate', type=str, dest='migrate', help='Migrate old posts.')
    parser.add_argument('--fix-summary', dest='fix_summary', help='Render new summary from posts.')
    args = parser.parse_args()
    print(f'Called with arguments: {args}')

    ROOTDIR = par_dir(BASEDIR)

    if args.new:
        raw_url = args.new
        problem_md = ''
        problem_slug = ''
        xxxcode = None
        convert_desc = True

        if raw_url.startswith('https://leetcode'):
            xxxcode = Leetcode()
        elif raw_url.startswith('https://www.lintcode.com'):
            xxxcode = Lintcode()
            convert_desc = False

        problem = xxxcode.get_problem_all(raw_url)
        problem_slug = slugify(problem['title'], separator="_")
        problem_md = problem2md(problem, convert_desc)

    if args.dir:
        post_dir = os.path.join(ROOTDIR, args.dir)
        post_fn = os.path.join(post_dir, f'{problem_slug}.md')
        summary_path = f"{args.dir.strip('/').split('/')[-1]}/{problem_slug}.md"
        summary_line = f'* [{problem["title"]}]({summary_path})'
        print(summary_line)
        mkdir_p(post_dir)
        with open(post_fn, 'w', encoding='utf-8') as f:
            print(f'Creating post file {post_fn}...')
            f.write(problem_md)

    if args.fix_summary:
        update_summary(ROOTDIR)

if __name__ == '__main__':
    main()