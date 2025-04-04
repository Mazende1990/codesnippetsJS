#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GitBook Algorithm Helper

A utility script for managing algorithm problem posts for GitBook.
Supports creating new posts from LeetCode/LintCode problems, updating existing posts,
and generating summaries.
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

# Constants
BASEDIR = os.path.abspath(os.path.dirname(__file__))
ROOTDIR = par_dir(BASEDIR)


def get_current_timestamp():
    """Return a formatted timestamp string for the current time."""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def create_new_problem_post(url, directory=None):
    """
    Create a new markdown post from a LeetCode or LintCode problem URL.
    
    Args:
        url (str): The LeetCode or LintCode problem URL
        directory (str, optional): Target directory for the markdown file
        
    Returns:
        tuple: (problem_data, markdown_content, slug)
    """
    problem_md = ''
    problem_slug = ''
    platform = None
    convert_description = True
    
    # Determine the platform and set up the appropriate client
    if url.startswith('https://leetcode'):
        platform = Leetcode()
    elif url.startswith('https://www.lintcode.com'):
        platform = Lintcode()
        convert_description = False
    else:
        raise ValueError(f"Unsupported problem URL: {url}")
    
    # Fetch the problem data and convert to markdown
    problem_data = platform.get_problem_all(url)
    problem_slug = slugify(problem_data['title'], separator="_")
    problem_md = problem2md(problem_data, convert_description)
    
    # Write to file if directory is specified
    if directory:
        post_dir = os.path.join(ROOTDIR, directory)
        post_filename = os.path.join(post_dir, f"{problem_slug}.md")
        
        # Create directory if it doesn't exist
        mkdir_p(post_dir)
        
        # Generate summary path and line for SUMMARY.md
        summary_path = f"{directory.strip('/').split('/')[-1]}/{problem_slug}.md"
        summary_line = f"* [{problem_data['title']}]({summary_path})"
        print(f"Summary line: {summary_line}")
        
        # Write the markdown content to file
        with open(post_filename, 'w', encoding='utf-8') as f:
            print(f"Creating post file: {post_filename}")
            f.write(problem_md)
    
    return problem_data, problem_md, problem_slug


def main():
    """Main function to parse arguments and execute commands."""
    parser = argparse.ArgumentParser(
        description='Helper utility for managing algorithm problems in GitBook format'
    )
    
    # Command-line arguments
    parser.add_argument(
        '--new', 
        type=str, 
        dest='new',
        help='Create new post with given LeetCode/LintCode URL'
    )
    parser.add_argument(
        '--dir', 
        type=str, 
        dest='dir',
        help='Create markdown file in the specified directory'
    )
    parser.add_argument(
        '--update', 
        nargs='*', 
        dest='update',
        help='Update post with given title in post and summary'
    )
    parser.add_argument(
        '--migrate', 
        type=str, 
        dest='migrate',
        help='Migrate old posts to the new format'
    )
    parser.add_argument(
        '--fix-summary', 
        action='store_true',
        dest='fix_summary',
        help='Regenerate SUMMARY.md from posts'
    )
    
    # Parse arguments
    args = parser.parse_args()
    print(f'Called with arguments: {args}')
    
    # Process commands
    if args.new:
        create_new_problem_post(args.new, args.dir)
    
    if args.fix_summary:
        update_summary(ROOTDIR)


if __name__ == '__main__':
    main()