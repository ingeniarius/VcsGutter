import sublime
import sublime_plugin
from view_collection import ViewCollection


class VcsGutterCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.view = self.window.active_view()
        if not self.view:
            # Sometimes GitGutter tries to run when there is no active window
            # and it throws an error because self.view is None.
            # I have only been able to reproduce this in the following scenario:
            # you clicked on FileA in the sidebar (FileA is not previously open)
            # 
            # not to open it but to preview it. While previewing it you press
            # ctrl+` to open a console. With the console selected and the
            # unopened FileA preview showing in the window you click on another
            # unopened file, FileB to preview that file. There will be no active
            # window at this time and GitGutter will throw an error. So we can
            # just skip running this time because immediately after selecting
            # FileB, focus will shift from the console to its preview. This will
            # cause GitGutter to run again on the FileB preview.
            # Wow that was a really long explanation.
            return
        self.clear_all()
        inserted, modified, deleted = ViewCollection.diff(self.view)
        self.lines_removed(deleted)
        self.lines_added(inserted)
        self.lines_modified(modified)

    def clear_all(self):
        self.view.erase_regions('vcs_gutter_deleted_top')
        self.view.erase_regions('vcs_gutter_deleted_bottom')
        self.view.erase_regions('vcs_gutter_inserted')
        self.view.erase_regions('vcs_gutter_changed')

    def lines_to_regions(self, lines):
        regions = []
        for line in lines:
            position = self.view.text_point(line - 1, 0)
            region = sublime.Region(position, position)
            regions.append(region)
        return regions

    def lines_removed(self, lines):
        bottom_lines = []
        for line in lines:
            if line != 1:
                bottom_lines.append(line - 1)
        self.lines_removed_top(lines)
        self.lines_removed_bottom(bottom_lines)

    def lines_removed_top(self, lines):
        regions = self.lines_to_regions(lines)
        scope = 'markup.deleted'
        icon = '../VCS Gutter/icons/deleted_top'
        self.view.add_regions('vcs_gutter_deleted_top', regions, scope, icon)

    def lines_removed_bottom(self, lines):
        regions = self.lines_to_regions(lines)
        scope = 'markup.deleted'
        icon = '../VCS Gutter/icons/deleted_bottom'
        self.view.add_regions('vcs_gutter_deleted_bottom', regions, scope, icon)

    def lines_added(self, lines):
        regions = self.lines_to_regions(lines)
        scope = 'markup.inserted'
        icon = '../VCS Gutter/icons/inserted'
        self.view.add_regions('vcs_gutter_inserted', regions, scope, icon)

    def lines_modified(self, lines):
        regions = self.lines_to_regions(lines)
        scope = 'markup.changed'
        icon = '../VCS Gutter/icons/changed'
        self.view.add_regions('vcs_gutter_changed', regions, scope, icon)
