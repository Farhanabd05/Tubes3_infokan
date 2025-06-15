# Aho-Corasick String Matching Algorithm
from collections import deque
class AhoCorasick:
    def __init__(self, words: list[str]):
        self.root = TrieNode()
        for word in words:
            self.root.add_word(word)
        self.build_failure_links()

    def build_failure_links(self):
        self.root.fail_link = self.root
        queue:deque[TrieNode] = deque()
        for child in self.root.children.values():
            child.fail_link = self.root
            queue.append(child)
        while queue:
            curr_node = queue.popleft()
            for char, child in curr_node.children.items():
                queue.append(child)
                curr_fail_link = curr_node.fail_link
                while char not in curr_fail_link.children.keys() and curr_fail_link !=self.root:
                    curr_fail_link = curr_fail_link.fail_link   
                child.fail_link = curr_fail_link.children.get(char, self.root)    
                child.output += child.fail_link.output
    
    @staticmethod
    def search(text:str, words:list[str]) -> list[tuple[int, str]]:
        """
        Searches for all occurrences of words in the text.
        Returns a list of tuples (index, word).
        """
        ac = AhoCorasick(words)
        results = []
        curr_node = ac.root
        for i, char in enumerate(text):
            if char in curr_node.children.keys():
                curr_node = curr_node.children[char]
                if curr_node.output:
                    for word in curr_node.output:
                        results.append((i - len(word)+1, word))
            elif curr_node == ac.root:
                continue
            else:
                curr_node = curr_node.fail_link
        return results
    
class TrieNode:
    def __init__(self):
        self.children:dict[str,TrieNode] = {}
        self.fail_link:TrieNode = None
        self.output = []
    
    def add_word(self,word:str):
        """
        Adds a word to the TrieNode.
        """
        node = self
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.output.append(word)