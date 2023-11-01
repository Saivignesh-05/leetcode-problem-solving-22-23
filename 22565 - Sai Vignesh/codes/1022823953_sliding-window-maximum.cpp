class Solution {
public:
    vector<int> maxSlidingWindow(vector<int>& nums, int k) {
        auto tmp = max_element(nums.begin(),nums.begin()+(k));
        // cout<<nums.size()<<endl;
        // cout<<*nums.begin()<<" "<<*(nums.begin()+(k-1))<<endl;
        int dist = distance(nums.begin(),tmp);
        pair<int,int> maxi(*tmp,dist);
        // cout<<maxi.first<<" "<<maxi.second;
        int i=1,j=k,lent = nums.size();
        vector<int> maxes = {*tmp};
        // cout<<j<<endl;
        while(j<lent)
        {
            if(nums[j] >= maxi.first){
                maxi = {nums[j],j};
            }
            else if(maxi.second<i)
            {
                tmp = max_element(nums.begin()+i,nums.begin()+j+1);
                while(tmp+1!=nums.begin()+j+1 && *tmp == *(tmp+1))
                    ++tmp;
                // cout<<*tmp<<" "<<*(tmp+1)<<endl;
                dist = distance(nums.begin(),tmp);
                maxi = {*tmp,dist};
            }
            maxes.push_back(maxi.first);
            ++i;++j;
        }
        return maxes;
        
    }
};