#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GitBook Algorithm Helper

This script helps manage algorithm problem posts for GitBook by:
- Creating new posts from LeetCode/LintCode URLs
- Updating existing posts
- Migrating old posts
- Fixing summary files
"""

import os
import argparse
from datetime import datetime
from pathlib import Path

import frontmatter
from slugify import slugify

from util import par_dir, mkdir_p
from leetcode import Leetcode
from lintcode import Lintcode
from summary import update_summary
from ojhtml2markdown import problem2md


class ProblemManager:
    """Manages algorithm problem posts and summaries."""
    
    def __init__(self):
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.rootdir = par_dir(self.basedir)
        
    @staticmethod
    def current_timestamp():
        """Return current time in YYYY-MM-DD_HH-MM-SS format."""
        return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    def create_new_post(self, url, target_dir):
        """
        Create a new problem post from a LeetCode/LintCode URL.
        
        Args:
            url: The problem URL
            target_dir: Directory to create the post in
            
        Returns:
            tuple: (problem_slug, problem_md, problem_data)
        """
        problem_data = self._fetch_problem_data(url)
        problem_slug = slugify(problem_data['title'], separator="_")
        convert_desc = not url.startswith('https://www.lintcode.com')
        problem_md = problem2md(problem_data, convert_desc)
        
        return problem_slug, problem_md, problem_data
    
    def _fetch_problem_data(self, url):
        """Fetch problem data from the appropriate platform."""
        if url.startswith('https://leetcode'):
            platform = Leetcode()
        elif url.startswith('https://www.lintcode.com'):
            platform = Lintcode()
        else:
            raise ValueError("Unsupported problem URL")
            
        return platform.get_problem_all(url)
    
    def save_post(self, dir_name, slug, content, title):
        """
        Save the problem post to a markdown file.
        
        Args:
            dir_name: Target directory name
            slug: Problem slug for filename
            content: Markdown content
            title: Problem title for summary
        """
        post_dir = os.path.join(self.rootdir, dir_name)
        post_path = os.path.join(post_dir, f"{slug}.md")
        summary_path = self._generate_summary_path(dir_name, slug)
        
        mkdir_p(post_dir)
        with open(post_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Created post file: {post_path}")
        print(self._generate_summary_line(title, summary_path))
    
    def _generate_summary_path(self, dir_name, slug):
        """Generate the summary path for a problem."""
        clean_dir = dir_name.strip('/')
        return f"{clean_dir.split('/')[-1]}/{slug}.md"
    
    def _generate_summary_line(self, title, path):
        """Generate the summary line for a problem."""
        return f"* [{title}]({path})"


def main():
    """Handle command line arguments and execute appropriate actions."""
    parser = argparse.ArgumentParser(
        description='Helper for managing GitBook algorithm posts',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument('--new', type=str, dest='new',
                       help='create new post with given leetcode/lintcode url')
    parser.add_argument('--dir', type=str, dest='dir',
                       help='target directory for new post')
    parser.add_argument('--update', nargs='*', dest='update',
                       help='update post with given title in post and summary')
    parser.add_argument('--migrate', type=str, dest='migrate',
                       help='migrate old posts')
    parser.add_argument('--fix-summary', action='store_true', dest='fix_summary',
                       help='regenerate summary from posts')
    
    args = parser.parse_args()
    print(f"Called with arguments: {args}")
    
    manager = ProblemManager()
    
    if args.new and args.dir:
        slug, md, problem = manager.create_new_post(args.new, args.dir)
        manager.save_post(args.dir, slug, md, problem['title'])
    
    if args.fix_summary:
        update_summary(manager.rootdir)


if __name__ == '__main__':
    main()