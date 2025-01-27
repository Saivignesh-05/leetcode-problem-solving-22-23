class Solution {
public:
    void merge(vector<int>& nums1, int m, vector<int>& nums2, int n) {
        int i,j=0;
        for(i=0;i<m && j<n;++i)
        {
            if(nums2[j]<=nums1[i])
            {
                nums1.insert(nums1.begin()+i,nums2[j++]);
                ++m;
                nums1.pop_back();
            }
        }
        for(;j!=n;++i,++j)
        {
            nums1.insert(nums1.begin()+i,nums2[j]);
            nums1.pop_back();
        }
            
        // cout<<nums1[0];
    }
};