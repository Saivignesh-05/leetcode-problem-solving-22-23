/**
 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     TreeNode *left;
 *     TreeNode *right;
 *     TreeNode() : val(0), left(nullptr), right(nullptr) {}
 *     TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
 *     TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
 * };
 */
class Solution {
public:
    bool isSameTree(TreeNode* p, TreeNode* q) {
        if(!p && !q) return true;
        if(!p || !q || p->val != q->val)
            return false;
        // both are not empty
        return isSameTree(p->left,q->right) && isSameTree(p->right,q->left);
    }

    bool isSymmetric(TreeNode* root) {
        if(!root) return true;        
        bool ans = isSameTree(root->left,root->right);
        root->right = root->left = NULL;
        return ans;
        
        
    }
};