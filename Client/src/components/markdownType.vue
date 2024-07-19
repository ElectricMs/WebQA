<template>
  <div>
    <div v-html="html" class="zxa"></div>
  </div>
</template>

<script>
import MarkdownIt from 'markdown-it';
import markdownItFootnote from 'markdown-it-footnote';
import markdownItTaskLists from 'markdown-it-task-lists';
import markdownItAbbr from 'markdown-it-abbr';
import markdownItContainer from 'markdown-it-container';
import hljs from 'highlight.js';
import markdownItHighlightjs from 'markdown-it-highlightjs';

export default {
  data() {
    return {
      markdown: `


** asdasdas：%%$$ **
** 快速排序   **算法是一种基于分治法的高效排序
以下是一个简单的快速排序算法的Python实现：

\`\`\`python
def quick_sort(arr):
    """
    快速排序主函数
    :param arr: 一个需要被排序的列表
    """
    if len(arr) <= 1:
        return arr
# 示例代码
example_array = [7, 2, 1, 6, 8, 5, 3, 4]
sorted_array = quick_sort(example_array)
print(sorted_array)
\`\`\`

这个代码实现了快速排序算法，其中\`quick_sort\`函数首



`,
      md: new MarkdownIt()
          .use(markdownItFootnote)
          .use(markdownItTaskLists, { enabled: true })
          .use(markdownItAbbr)
          .use(markdownItContainer, 'warning')
          .use(markdownItHighlightjs, { hljs }), // 添加 markdown-it-highlightjs 插件
    }
  },
  computed: {
    html() {
      this.markdown = this.markdown.replace(/\*\*\s*([^*]*?)\s*(:\s*)?\*\*/g, '**$1$2**');
      return this.md.render(this.markdown);
    }
  }
}
</script>
<style scoped>
.zxa {
  margin: auto;
  width: 600px;
}

::v-deep .zxa pre .hljs {
  border-radius: 10px !important; /* 圆角 */
  /* 其他你想要的样式 */
  padding: 1em; /* 例子中的内边距 */
  background-color: #f5f5f5; /* 例子中的背景色 */
}
</style>
