#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to manage algorithm posts for GitBook-style organization.

Supports:
- Creating new posts from Leetcode/Lintcode URLs
- Organizing them into directories
- Updating summaries
- Migrating old posts
"""

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

# Base directory of the current file
BASEDIR = os.path.abspath(os.path.dirname(__file__))


def curr_time():
    """Returns current timestamp as a formatted string."""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def handle_new_post(raw_url):
    """
    Fetches the problem data from Leetcode or Lintcode
    and converts it to markdown.
    """
    if raw_url.startswith('https://leetcode'):
        provider = Leetcode()
        convert_desc = True
    elif raw_url.startswith('https://www.lintcode.com'):
        provider = Lintcode()
        convert_desc = False
    else:
        raise ValueError("Unsupported URL. Only Leetcode and Lintcode are supported.")

    problem = provider.get_problem_all(raw_url)
    problem_slug = slugify(problem['title'], separator="_")
    problem_md = problem2md(problem, convert_desc)

    return problem, problem_slug, problem_md


def write_post_to_dir(root_dir, relative_dir, slug, markdown, title):
    """
    Writes the markdown content to the correct directory and file.
    Also prints the line to be inserted into the summary.
    """
    post_dir = os.path.join(root_dir, relative_dir)
    post_fn = os.path.join(post_dir, slug + '.md')
    summary_path = os.path.join(relative_dir.strip('/'), slug + '.md')

    summary_line = f'* [{title}]({summary_path})'
    print(summary_line)

    mkdir_p(post_dir)
    with open(post_fn, 'w', encoding='utf-8') as f:
        print(f'Creating post file: {post_fn}')
        f.write(markdown)


def main():
    parser = argparse.ArgumentParser(description='Helper for GitBook algorithm post management')
    parser.add_argument('--new', type=str, dest='new', help='Create a new post from a Leetcode/Lintcode URL.')
    parser.add_argument('--dir', type=str, dest='dir', help='Target directory for new markdown file.')
    parser.add_argument('--update', nargs='*', dest='update', help='Update post(s) by title.')
    parser.add_argument('--migrate', type=str, dest='migrate', help='Migrate old posts.')
    parser.add_argument('--fix-summary', dest='fix_summary', help='Regenerate summary from posts.')
    args = parser.parse_args()

    print(f'Called with arguments: {args}')
    root_dir = par_dir(BASEDIR)

    # Handle creating a new post
    if args.new:
        problem, slug, markdown = handle_new_post(args.new)

        if args.dir:
            write_post_to_dir(root_dir, args.dir, slug, markdown, problem['title'])

    # Handle summary regeneration
    if args.fix_summary:
        update_summary(root_dir)


if __name__ == '__main__':
    main()
