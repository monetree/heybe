from settings.settings import myclient, mydb
from bson.json_util import dumps
import re
import json
import math
from datetime import *
from statistics import mean
from .utils import dict_merger, dict_merger2
import random
from dateutil.relativedelta import relativedelta
from operator import itemgetter
from collections import Counter
from brand.utils import red
import bisect
from django.http import JsonResponse


Cname_EugenieTable_Brand="NR_Exp_Brand_Normalized_Table_"

Cname_EugenieTable="NR_Exp_Normalized_Table_"
Cname_ForecastTable="Forecast_Table_"
Cname_NeedstateTable="NAC_Exp_Needstate_Table_"
Cname_LS1="NAC_Exp_Needstate_Table_"
Cname_LS2="NAC_Exp_Viral_Table_"


class Utils:
    def association_chart_limited(request, needstate):
        category      = request.GET.get('category')
        channel       = request.GET.get('channel').replace("_","")
        country       = request.GET.get('country')
        keyword       = request.GET.get('keyword')
        sentikey       = request.GET.get('sentikey')
        sentiment   = request.GET.get('sentiment')

        #to remove later
        if needstate == "sub":
            needstate = "sub format"

        if needstate == "fragrance/":
            needstate = "fragrance"

        if sentiment is None:
            sentikey_all=["Pos","Neg","Neu"]
        elif sentiment == 'null':
            sentikey_all=["Pos","Neg","Neu"]
        else:
            if sentiment == "neutral":
                sentikey_all=["Neu"]
            elif sentiment == "negative":
                sentikey_all=["Neg"]
            elif sentiment == "positive":
                sentikey_all=["Pos"]
            else:
                sentikey_all=["Pos","Neg","Neu"]

        if channel=="all":
            channel="All"

        if category is None:
            return {"code":400, "msg":"category Required"}
        if country is None:
            return {"code":400, "msg":"country Required"}
        if channel is None:
            return {"code":400, "msg":"channel Required"}

        mydb   = myclient[category]
        mycol  = mydb['association_keywords_count_'+country]
        
        if sentikey:
            sentikey_all=[sentikey]
        
        if "Need_state_A" in json.loads(dumps(mycol.find().limit(1)))[0]:
            nscolA="Need_state_A"
            nscolB="Need_state_B"
        else:
            nscolA="Need state_A"
            nscolB="Need state_B"

        if needstate:
            query = {"site_type": channel, nscolA: needstate,"antecedent_lab":{"$in":sentikey_all},"period_sum":{"$in":[3,2]}}
            need = {"_id": 0, nscolA: 1, nscolB: 1, "consequents": 1, "consequents_count": 1}
        
        if keyword:
            if keyword != 'null':
                query = {"site_type": channel,"antecedent":{"$in" : keyword.split(",")}, nscolA: needstate,"antecedent_lab":{"$in":sentikey_all},"period_sum":{"$in":[3,2]}}
                need = {"_id": 0, nscolA: 1, nscolB: 1, "consequents": 1, "consequents_count": 1}

        res = mycol.find(query,need)
        res = json.loads(dumps(res))

        NS_total_list = {}

        for i in res:
            for j in range(len(i['consequents'])):
                    if i[nscolB][j] is not None:
                        nsname=i[nscolB][j]+"__"+i['consequents'][j]
                        nsval=i['consequents_count'][j]

                        if nsname in NS_total_list.keys(): 
                            NS_total_list[nsname]=NS_total_list[nsname]+nsval
                        else:
                            NS_total_list.update({nsname:nsval})
        
        final_res = []
        for i in NS_total_list:
            key=i.split("__")[0]
            value=i.split("__")[1]
            support=NS_total_list[i]
            final_res.append({"key":key, "value": value,"support":support})

        
        topNS=[];
        ns=[i['key'] for i in final_res]
        ns=set(ns)
        ns=list(ns)

        for n in ns:
            tempn=[i for i in final_res if i['key']==n]
            temp=[j["support"] for j in tempn]
            temp=sum(temp) / len(temp)
            topNS.append({"NS":n,"value":temp})


        
        
        NSlist=[i['NS'] for i in topNS]
        NSlist=NSlist[:min(7,len(NSlist))]

        
        final_res=sorted(final_res, key=lambda x:x['support'],reverse=True)
        final_res=final_res[:min(30,len(final_res))]

        if keyword != 'null' and keyword:
            topNS=[i['key'] for i in final_res]
        else:  
            topNS=[i['key'] for i in final_res if i['key']!=needstate]
        topNS=list(set(topNS))
        topNS=topNS[:(min(10,len(topNS)))]
        
        
        final_res=[i for i in final_res if i['key'] in topNS]
        top_comb=final_res[:6]


        valrange=[i['support'] for i in final_res]
        minv=min(valrange)
        maxv=max(valrange)
        maxmin=maxv-minv

        range_color_val=[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
        range_color_map=["#D0DA75","#A2D05F","#6FC44D","#3CB73E","#2CA955","#178A76","#127779","#0D5468","#093656","#061E43"]
                    
           
        for i in final_res:
            i['support']=round((i['support']-minv)/maxmin,2)
            i['color']="style='color:"+range_color_map[bisect.bisect_left(range_color_val,i['support'])-1]+"'"
            if i['support']<0.1:
                i['color']="style='color:"+"#D0DA75"+"'"
            if  i['support']>0.66:
                i['support']="H"
            elif i['support']>0.33:
                i['support']="M"
            else:
                i['support']="L"

 
        notinc=[i['key'] for i in top_comb]
        
        # ["<span class='keywords'>{}</span>".format(j)+"<span class='pink'> - </span>"+"<span class='supports' "+c+'>'+"{}</span>".format(str(f))]
        
        k={}
        countl={}
        for ele in final_res:
            i,j,f,c=(ele["key"],ele['value'],ele['support'],ele['color'])
            if not k.get(i):
                k[i]=["<span class='keywords'>{}</span>".format(j)+"<span class='supports' "+c+'>'+"{}</span>".format(str(f))]
            else:
                k[i].append("<span class='keywords'>{}</span>".format(j)+"<span class='supports' "+c+'>'+"{}</span>".format(str(f)))

            if not countl.get(i):
                countl[i]=[f]
            else:
                countl[i].append(f)

        countdictM=[]
        countdictL=[]
        for i in countl:
            if i not in notinc:
                if len(countl[i]) > 5:
                    countl[i]= countl[i][:5] 

                countdictM.append({'ns':i,"val":len([j for j in countl[i] if j=="M"])})
                countdictL.append({'ns':i,"val":len([j for j in countl[i] if j=="L"])})
            

        countdictM=sorted(countdictM, key = lambda i: i['val'],reverse=True) 
        countdictL=sorted(countdictL, key = lambda i: i['val'],reverse=True) 
        finalalsoNS=list(set([countdictM[0]['ns'],countdictL[0]['ns']]))   

        final_res = [{"key":x[0],"value":",".join(x[1]).replace(",","<br/>").split("<br/>")} for x in k.items()]
        
        for i in final_res:
            if len(i["value"]) > 5:
                i["value"] = i["value"][:5]
        for i in final_res:
            i["value"] = "<br/>".join(i["value"])      
        
        stmnt=""
       
        try:
            return top_comb
        except IndexError:
            return []

    def top_keywords(request, needstate):
        category          = request.GET.get('category')
        channel = request.GET.get('channel')
        country = request.GET.get('country')
        metric=  request.GET.get('metric')

        mydb   = myclient[category]
        mycol  = mydb[Cname_EugenieTable + country]
        mycol2 = mydb[Cname_NeedstateTable + country]

        if needstate is None:
            return {"code":400, "msg":"needstate Required"}


        if channel=="all":
            channelEmerg="all"
            AbsM="$"+metric
        else: 
            channelEmerg=channel.replace("_","")
            AbsM="$"+metric+channel
        
        #         # TO BE DELETED LATER
        # if (category == "Surface_care" and country == "IND"):
        #     if channel == 'all':
        #         channelEmerg="Abs"
        #     else:
        #         channelEmerg = "Abs"+channelEmerg

        qu = mycol2.find({"channel":channelEmerg})
        qu.batch_size(50000)
        x=json.loads(dumps(qu))
        qu.close()
        lsdates= mycol2.find({"channel":channelEmerg}).distinct('latest_date')
        lsdates=json.loads(dumps(lsdates))
        lsdates.sort()
        lsdates=lsdates[-1]
        x=[i for i in x if i['latest_date']==lsdates]

        driving_keyword = []

        try:
            emerging_needstates = x[0]['emerging_needstates'][needstate][1]['emerging_keywords']
            driving_keyword = [{e[1]:e[3]} for e in emerging_needstates]
        except KeyError:
            pass

        try:
            emerging_parent_keywords = x[0]['emerging_parent_keywords']
            if emerging_parent_keywords:
                for i in emerging_parent_keywords:
                    driving_keyword.append({i[0]:i[3]})
        except KeyError:
            pass

        ld = mycol.find().sort('Date', -1).limit(1)
        rd = json.loads(dumps(ld, indent=2))
        latest_date_str =rd[0]['Date']
        latest_date = datetime.strptime(latest_date_str, '%Y-%m-%d')
        today       = latest_date


        three_month = relativedelta(months=3)
        six_month   = relativedelta(months=6)
        one_year    = relativedelta(months=12)
        two_year    = relativedelta(months=24)
        

        three_months_back_date  = today - three_month
        six_months_back_date    = today - six_month
        one_year_back_date      = today - one_year

        three_months_back_date_from_three_month = today - three_month - three_month
        six_months_back_date_from_six_months    = today - six_month - six_month
        one_year_back_date_from_one_year        = today - one_year - six_month

        today = str(today.isoformat())
        three_months_back_date = str(three_months_back_date.isoformat())
        six_months_back_date = str(six_months_back_date.isoformat())
        one_year_back_date = str(one_year_back_date.isoformat())
        three_months_back_date_from_three_month = str(three_months_back_date_from_three_month.isoformat())
        six_months_back_date_from_six_months = str(six_months_back_date_from_six_months.isoformat())
        one_year_back_date_from_one_year = str(one_year_back_date_from_one_year.isoformat())

        projectnull = {
                 '$project': {
                        '_id': 1,
                        'total_abs': { '$ifNull': [ "$total_abs", 0 ] }
                            }
                    }

        if metric=='Abs':
            group = {
                "$group" : {
                        "_id" : "$Keyword", "total_abs": { "$sum" : AbsM }
                    }
                }
        else:
            group = {
                "$group" : {
                        "_id" : "$Keyword", "total_abs": { "$avg" : AbsM }
                    }
                }

        # mongo_date_formatter = {
        #     "$addFields": {
        #         "Date": {
        #             "$dateFromString": {
        #                 "dateString": "$Date",
        #                 "format": "%d/%m/%Y"
        #             }
        #         }
        #     }
        # }

   

    

        query_for_today_to_last_six_months = mycol.aggregate([
            # mongo_date_formatter,
            {
                "$match": {
                    'Keyword' : {"$ne" : None},
                    'Need state': needstate,
                    "Date": { "$gte": six_months_back_date, "$lt": today }
                }
            },
            group,
            projectnull
        ])
        query_for_today_to_last_six_months.batch_size(50000)

        query_for_last_six_months_to_next_six_months = mycol.aggregate([
            # mongo_date_formatter,
            {
                "$match": {
                    'Keyword' : {"$ne" : None},
                    'Need state': needstate,
                    "Date": { "$gte": six_months_back_date_from_six_months, "$lt": six_months_back_date }
                }
            },
            group,
            projectnull
        ])
        query_for_last_six_months_to_next_six_months.batch_size(50000)






        res_for_today_to_last_six_months               = json.loads(dumps(query_for_today_to_last_six_months))
        res_for_last_six_months_to_next_six_months     = json.loads(dumps(query_for_last_six_months_to_next_six_months))


        query_for_today_to_last_six_months.close()
        query_for_last_six_months_to_next_six_months.close()

        api = {
            "category" : category,
            "six_month"   : []
        }


        res_for_today_to_last_six_months = [{'_id':ele['_id'],'total':[ele['total_abs'],ele1['total_abs']]} for ele in res_for_today_to_last_six_months for ele1 in res_for_last_six_months_to_next_six_months if ele['_id']==ele1['_id']]


  

        six_month = res_for_today_to_last_six_months
        if len(six_month) > 0:
            for i in six_month:
                # if i['total'][0] == 0:
                if (i['total'][1] == 0 and i['total'][0] == 0 ):
                    i['percentage'] = int(0)
                elif i['total'][1] == 0 :
                    i['percentage'] = -99999
                else:
                    i['percentage'] = int((i['total'][0]/i['total'][1]-1)*100)
            for i in six_month:del i["total"]

        for i in six_month:
            i['six_month_percentage'] = i['percentage']
            i['needstate'] = i["_id"]
            del i["_id"]


        for i in six_month:
            del i['percentage']



        if driving_keyword:
            for i in six_month:
                for j in driving_keyword:
                    if i['needstate'] in j.keys() and 'Negative' in j.values():
                        i['driving'] = "d"
                        break
                    elif i['needstate'] in j.keys() and 'Positive' in j.values():
                        i['driving'] = "a"
                        break
                    else:
                        i['driving'] = "n"
                        
        else:
            for i in six_month:
                i['driving'] = "n"

        if x:
            try:
                six_month=sorted(six_month, key=lambda i:(i['driving'], -i['six_month_percentage']))
            except KeyError:   
                pass    
        else:
            six_month=sorted(six_month,key=lambda i:(-i['six_month_percentage']))

        for i in six_month:
            if i['six_month_percentage']==-99999:
                i['six_month_percentage']='inf'
        return six_month

    def brand_split_chart(request, needstate):
        category = request.GET.get('category')
        country = request.GET.get('country')
        brandlist = request.GET.get('brands')
        channel   = request.GET.get('channel').replace("_","")

        mydb   = myclient[category]
        mycol  = mydb[Cname_EugenieTable_Brand + country]

        if needstate:
            needstate = needstate.replace("/","")

        if channel=="all":
            abs_channel="$Abs"
            PoS_M="$PoS_M"
            Neutral="$Neutral"
            Neg_M="$Neg_M"
        else:
            abs_channel="$Abs_"+channel
            PoS_M="$PoS_M"+channel
            Neutral="$Neutral"+channel
            Neg_M="$Neg_M"+channel
    
        needs    = {abs_channel:1,"_id":0,"Need state":1,"Date":1,"Category":1,"Brands":1}
        
        colors = []
        ld = mycol.find().sort('Date', -1).limit(1)
        rd = json.loads(dumps(ld, indent=2))
        
        if rd:
            latest_date_str =rd[0]['Date']
            latest_date = datetime.strptime(latest_date_str, '%Y-%m-%d')

            three_months= relativedelta(months=6)
            three_months_back_date=latest_date-three_months
            three_months_back_date=str(three_months_back_date.isoformat())
            latest_date=str(latest_date.isoformat())

            if needstate:
                query = mycol.aggregate([
                    {
                        "$match": {
                            'Keyword':None,
                            'Need state':needstate,
                            "Date": { "$gte":  three_months_back_date, "$lt": latest_date },
                            "Brands":{"$ne":"No brand"},
                            
                        }
                    },
                    {
                    "$group" : {
                    "_id" : {"Brand":"$Brands"},
                        "total_abs": { "$sum" : abs_channel },
                        "t_P":{"$sum": PoS_M}, 
                        "t_N":{"$sum": Neutral},
                        "t_Neg":{"$sum": Neg_M},
                        }
                    }])
            else:
                query = mycol.aggregate([
                    {
                        "$match": {
                            'Keyword':None,
                            
                            "Date": { "$gte":  three_months_back_date, "$lt": latest_date },
                            "Brands":{"$ne":"No brand"},
                            
                        }
                    },
                    {
                    "$group" : {
                    "_id" : {"Brand":"$Brands"},
                        "total_abs": { "$sum" : abs_channel },
                        "t_P":{"$sum": PoS_M}, 
                        "t_N":{"$sum": Neutral},
                        "t_Neg":{"$sum": Neg_M},
                        }
                    }])

            data = json.loads(dumps(query))
            query.close()
            

            total_overall=sum([i['total_abs'] for i in data])

            own_brands=['finish','air wick','vanish','lysol','harpic','mortein']

            if category=="Surface_care":
                own_brand="lysol"
            elif category=="Air_care":
                own_brand="air wick"
            elif category=="Fabric_care":
                own_brand="vanish"
            elif category=="Dish_care":
                own_brand="finish"            
            elif category=="Toilet_care":
                own_brand="harpic"     
            elif category=="Pest_care":
                own_brand="mortein"    

       
            if brandlist:
                brandlist=list(set([own_brand]+ brandlist.split(",")))
                data=sorted(data, key = lambda k:k['total_abs'],reverse=True)
                for i in data:
                    if i["_id"]['Brand'] not in brandlist:
                        i["_id"]['Brand']="others"

                res=[{'brand':i["_id"]['Brand'],'value':i['total_abs'],
                "perc": float(0 if total_overall==0 else round(i['total_abs']*100/total_overall,2)),
                "t_P":i['t_P'],
                "t_N":i['t_N'],
                "t_Neg":i['t_Neg'],
                "perc_t_P":float(0 if total_overall==0 else round(i['t_P']*100/total_overall,2)),
                "perc_t_N":float(0 if total_overall==0 else round(i['t_N']*100/total_overall,2)),
                "perc_t_Neg":float(0 if total_overall==0 else round(i['t_Neg']*100/total_overall,2)),
                } for i in data if i["_id"]['Brand'] in brandlist]

                total_others=sum([i['total_abs'] for i in data if i["_id"]['Brand']=="others"])
                t_P_others=sum([i['t_P'] for i in data if i["_id"]['Brand']=="others"])
                t_N_others=sum([i['t_N'] for i in data if i["_id"]['Brand']=="others"])
                t_Neg_others=sum([i['t_Neg'] for i in data if i["_id"]['Brand']=="others"])
                res.append({'brand':'others','value':total_others,
                    'perc': float(0 if total_overall==0 else round(total_others*100/total_overall,2)),
                    "t_P":t_P_others,
                    "t_N":t_N_others,
                    "t_Neg":t_Neg_others,

                    })

                

            else:
                data=sorted(data, key = lambda k:k['total_abs'],reverse=True)
                lindex=min(7,len(data))

                owndata=[i for i in data if i["_id"]['Brand']==own_brand]
                

                res=[{'brand':i["_id"]['Brand'],'value':i['total_abs'],
                "perc": float(0 if total_overall==0 else round(i['total_abs']*100/total_overall,2)),
                "t_P":i['t_P'],
                "t_N":i['t_N'],
                "t_Neg":i['t_Neg'],
                "perc_t_P":float(0 if total_overall==0 else round(i['t_P']*100/total_overall,2)),
                "perc_t_N":float(0 if total_overall==0 else round(i['t_N']*100/total_overall,2)),
                "perc_t_Neg":float(0 if total_overall==0 else round(i['t_Neg']*100/total_overall,2)),
                } for i in data[0:lindex]+owndata]
                
                otherdata=[i for i in data[lindex:len(data)] if i["_id"]['Brand']!=own_brand]

                total_others=sum([i['total_abs'] for i in otherdata ])
                t_P_others=sum([i['t_P'] for i in otherdata])
                t_N_others=sum([i['t_N'] for i in otherdata])
                t_Neg_others=sum([i['t_Neg'] for i in otherdata])
                res.append({'brand':'others','value':total_others,
                    'perc': float(0 if total_overall==0 else round(total_others*100/total_overall,2)),
                    "t_P":t_P_others,
                    "t_N":t_N_others,
                    "t_Neg":t_Neg_others,

                    })
            return res
        else:
            return []
       
class CategoryView:
    def keyword_filter(request):
        category = request.GET.get('category')
        country = request.GET.get('country')
        brandlist = request.GET.get('brands')
        mydb   = myclient[category]
        mycol  = mydb[Cname_EugenieTable_Brand + country]
        channel   = request.GET.get('channel').replace("_","")
        needstate   = request.GET.get('needstate').needstate.replace("/","")


        if channel=="all":
            abs_channel="$Abs"
            PoS_M="$PoS_M"
            Neutral="$Neutral"
            Neg_M="$Neg_M"
        else:
            abs_channel="$Abs_"+channel
            PoS_M="$PoS_M"+channel
            Neutral="$Neutral"+channel
            Neg_M="$Neg_M"+channel
    
        needs    = {abs_channel:1,"_id":0,"Need state":1,"Date":1,"Category":1,"Brands":1}
        
        colors = []
        ld = mycol.find().sort('Date', -1).limit(1)
        rd = json.loads(dumps(ld, indent=2))
        

        if rd:
            latest_date_str =rd[0]['Date']
            latest_date = datetime.strptime(latest_date_str, '%Y-%m-%d')

            three_months= relativedelta(months=6)
            three_months_back_date=latest_date-three_months
            three_months_back_date=str(three_months_back_date.isoformat())
            latest_date=str(latest_date.isoformat())

            if needstate:
                query = mycol.aggregate([
                    {
                        "$match": {
                            'Keyword':None,
                            'Need state':needstate,
                            "Date": { "$gte":  three_months_back_date, "$lt": latest_date },
                            "Brands":{"$ne":"No brand"},
                            
                        }
                    },
                    {
                    "$group" : {
                    "_id" : {"Brand":"$Brands"},
                        "total_abs": { "$sum" : abs_channel },
                        "t_P":{"$sum": PoS_M}, 
                        "t_N":{"$sum": Neutral},
                        "t_Neg":{"$sum": Neg_M},
                        }
                    }])
            else:
                query = mycol.aggregate([
                    {
                        "$match": {
                            'Keyword':None,
                            
                            "Date": { "$gte":  three_months_back_date, "$lt": latest_date },
                            "Brands":{"$ne":"No brand"},
                            
                        }
                    },
                    {
                    "$group" : {
                    "_id" : {"Brand":"$Brands"},
                        "total_abs": { "$sum" : abs_channel },
                        "t_P":{"$sum": PoS_M}, 
                        "t_N":{"$sum": Neutral},
                        "t_Neg":{"$sum": Neg_M},
                        }
                    }])

            data = json.loads(dumps(query))
            query.close()
            

            total_overall=sum([i['total_abs'] for i in data])

            own_brands=['finish','air wick','vanish','lysol','harpic','mortein']

            if category=="Surface_care":
                own_brand="lysol"
            elif category=="Air_care":
                own_brand="air wick"
            elif category=="Fabric_care":
                own_brand="vanish"
            elif category=="Dish_care":
                own_brand="finish"            
            elif category=="Toilet_care":
                own_brand="harpic"     
            elif category=="Pest_care":
                own_brand="mortein"    


       
            if brandlist:
                brandlist=list(set([own_brand]+ brandlist.split(",")))
                data=sorted(data, key = lambda k:k['total_abs'],reverse=True)
                for i in data:
                    if i["_id"]['Brand'] not in brandlist:
                        i["_id"]['Brand']="others"
                        if i["_id"]['Brand']==own_brand:
                            i["_id"]['Brand']="['bold #ea3592]"+own_brand+"[/]"


                res=[{'brand':i["_id"]['Brand'],'value':i['total_abs'],
                "perc": float(0 if total_overall==0 else round(i['total_abs']*100/total_overall,2)),
                "t_P":i['t_P'],
                "t_N":i['t_N'],
                "t_Neg":i['t_Neg'],
                "perc_t_P":float(0 if total_overall==0 else round(i['t_P']*100/total_overall,2)),
                "perc_t_N":float(0 if total_overall==0 else round(i['t_N']*100/total_overall,2)),
                "perc_t_Neg":float(0 if total_overall==0 else round(i['t_Neg']*100/total_overall,2)),
                } for i in data if i["_id"]['Brand'] in brandlist]

                total_others=sum([i['total_abs'] for i in data if i["_id"]['Brand']=="others"])
                t_P_others=sum([i['t_P'] for i in data if i["_id"]['Brand']=="others"])
                t_N_others=sum([i['t_N'] for i in data if i["_id"]['Brand']=="others"])
                t_Neg_others=sum([i['t_Neg'] for i in data if i["_id"]['Brand']=="others"])
                res.append({'brand':'others','value':total_others,
                    'perc': float(0 if total_overall==0 else round(total_others*100/total_overall,2)),
                    "t_P":t_P_others,
                    "t_N":t_N_others,
                    "t_Neg":t_Neg_others,

                    })

                

            else:
                data=sorted(data, key = lambda k:k['total_abs'],reverse=True)
                lindex=min(7,len(data))

                owndata=[i for i in data if i["_id"]['Brand']==own_brand]
                for i in owndata:
                    if i["_id"]['Brand']==own_brand:
                            i["_id"]['Brand']="['bold #ea3592]"+own_brand+"[/]"

                

                res=[{'brand':i["_id"]['Brand'],'value':i['total_abs'],
                "perc": float(0 if total_overall==0 else round(i['total_abs']*100/total_overall,2)),
                "t_P":i['t_P'],
                "t_N":i['t_N'],
                "t_Neg":i['t_Neg'],
                "perc_t_P":float(0 if total_overall==0 else round(i['t_P']*100/total_overall,2)),
                "perc_t_N":float(0 if total_overall==0 else round(i['t_N']*100/total_overall,2)),
                "perc_t_Neg":float(0 if total_overall==0 else round(i['t_Neg']*100/total_overall,2)),
                } for i in data[0:lindex]+owndata]
                
                otherdata=[i for i in data[lindex:len(data)] if i["_id"]['Brand']!=own_brand]

                total_others=sum([i['total_abs'] for i in otherdata ])
                t_P_others=sum([i['t_P'] for i in otherdata])
                t_N_others=sum([i['t_N'] for i in otherdata])
                t_Neg_others=sum([i['t_Neg'] for i in otherdata])
                res.append({'brand':'others','value':total_others,
                    'perc': float(0 if total_overall==0 else round(total_others*100/total_overall,2)),
                    "t_P":t_P_others,
                    "t_N":t_N_others,
                    "t_Neg":t_Neg_others,

                    })
                
                

            return res
        else:
            return [] 

    def countries(request):
        category  = request.GET.get('category')
        mydb   = myclient[category]
        collection = mydb.collection_names(include_system_collections=False)
        countries = [i for i in list(set([i.split("_")[-1] for i in collection])) if i.isupper() and len(i) == 3]
        return countries

    def channels(request):
        category  = request.GET.get('category')
        country   = request.GET.get('country')
        mydb   = myclient[category]
        mycol  = mydb[Cname_EugenieTable + country]     
        res= json.loads(dumps(mycol.find({},{"_id":0}).limit(1)))
        res=list(res[0].keys())
        res=[i.split("_")[1] for i in res if i.startswith('SoV_')]
        res=[i for i in res if i!="General news Magazine"]
        return res

    def most_mentioned_channel(request):
        category  = request.GET.get('category')
        country = request.GET.get('country')
        
        mydb   = myclient[category]
        mycol  = mydb[Cname_EugenieTable + country]     
        channels = CategoryView.channels(request)
        mentions = []
        for i in channels:
            query = mycol.aggregate([
                {
                "$group" : {
                        "_id" : None,
                         "abs": { "$sum" : "$Abs_"+i }
                    }
                },{
                    "$sort":{
                        "abs":1
                    }
                }
            ])
            res = json.loads(dumps(query))
            mentions.append({
                "channel":i,
                "mentions":res[0]['abs']
            })
        length = len(mentions)
        
        for i in range(length-1):
            if mentions[i]['mentions'] > mentions[i+1]['mentions']:
                temp = mentions[i]
                mentions[i] = mentions[i+1]
                mentions[i+1] = temp
        return mentions[-1]

    def keyword_level_sentiment(request, needstatearg=None):
        category  = request.GET.get('category')
        country   = request.GET.get('country')
        channel   = request.GET.get('channel').replace("_","")
        if needstatearg:
            needstate = needstatearg
        else:
            needstate = request.GET.get('needstate')
        keyword   = request.GET.get('keyword')
        brand   = request.GET.get('brand')


        if channel == 'all':
            PoS_M = "$PoS_M"
            Neg_M = "$Neg_M"
            Neutral = "$Neutral"
        else:
            PoS_M = "$PoS_M"+channel
            Neg_M = "$Neg_M"+channel
            Neutral = "$Neutral"+channel

        if keyword == 'null':
            keyword = None
        elif not keyword:
            keyword = None
        else:
            keyword = keyword

        
        
        mydb   = myclient[category]
        if brand:
            mycol  = mydb[Cname_EugenieTable_Brand + country]
        else:
            mycol  = mydb[Cname_EugenieTable + country]


        ld = mycol.find().sort('Date', -1).limit(1)
        rd = json.loads(dumps(ld, indent=2))
        latest_date_str =rd[0]['Date']
        latest_date =datetime.strptime(latest_date_str, '%Y-%m-%d')
        one_months=relativedelta(months=6)
        one_months_back_date = latest_date - one_months

        latest_date = str(latest_date.isoformat())
        six_months_back_date = str(one_months_back_date.isoformat())

        group = {
                "$group" : {
                        "_id" : None,
                         "total_pos": { "$sum" : PoS_M },
                         "total_neg": { "$sum" : Neg_M },
                         "total_neu": { "$sum" : Neutral },
                    }
                }
        if brand:  
            if keyword:  
                match = {
                    "$match": {
                        "Date": { "$gte":  six_months_back_date, "$lte": latest_date },                        
                        "Need state": needstate,
                        "Brands":brand,
                        "Keyword":{"$in" : keyword.split(",")}
                    }
                }
            else:
                match = {
                    "$match": {
                        "Date": { "$gte":  six_months_back_date, "$lte": latest_date },
                        "Need state": needstate,
                        "Brands":brand
                    }
                }
        else:
            if keyword:
                match = {
                    "$match": {
                        "Date": { "$gte":  six_months_back_date, "$lte": latest_date },
                        "Need state": needstate,
                        "Keyword":{"$in" : keyword.split(",")}
                    }
                }
            else:
                match = {
                    "$match": {
                        "Date": { "$gte":  six_months_back_date, "$lte": latest_date },
                        "Need state": needstate
                    }
                }
        query = mycol.aggregate([
            match,
            group
        ])
        res = json.loads(dumps(query))
        for i in res:
            del i["_id"]
            i["year"] = "title"
        
        tot=res[0]['total_pos']+res[0]['total_neg']+res[0]['total_neu']
        res[0]['total_pos']=round(res[0]['total_pos']*100/tot,1)
        res[0]['total_neg']=round(res[0]['total_neg']*100/tot,1)
        res[0]['total_neu']=round(res[0]['total_neu']*100/tot,1)
        return res

    # database logic for categoryview -> social
    def social(request):
        category  = request.GET.get('category')
        page      = request.GET.get('page')
        limit     = request.GET.get('limit')
        country   = request.GET.get('country')
        channel   = request.GET.get('channel')
        needstate = request.GET.get('needstate')
        search    = request.GET.get('search')
        keyword   = request.GET.get('keyword')
        sentiment = request.GET.get('sentiment')

        if sentiment == 'positive':
            gt = 0.25
            lt = 1.1
            sflag=-1
        elif sentiment == 'neutral':
            gt = -0.25
            lt = 0.25
            sflag=-1
        elif sentiment == 'negative':
            gt = -1.1
            lt = -0.25
            sflag=1
        else:
            gt = -10
            lt = 10
            sflag=-1




        mydb   = myclient[category]
        mycol  = mydb["chatter_master_data_" + country]
        # mycol2 = mydb["NS_toDoc_mapping_" + country]
        mycol2 = mydb["NS_toDoc_mapping_table_" + country]
        join  =  "chatter_master_data_" + country


        if channel is not None:
            if channel == 'all':
                channel = None
            elif len(channel.split("_")) > 1:
                channel = channel.split("_")[1]

        if channel:
            query = {"site_type": channel }
        else:
            query = {}
        

        if channel is None:
            if search == "null" or len(search) < 1:
                lookup_match = None
            else:
                lookup_match = {
                            "$match" : {
                                    "inventory_docs.content": {"$regex" : re.compile(search, re.IGNORECASE)}
                                }
                            }
        else:
            if search == "null" or len(search) < 1:
                lookup_match = {
                        "$match" : {
                            # "inventory_docs.site_type": {"$regex" : re.compile(channel, re.IGNORECASE)},
                        }
                    }
            else:
                lookup_match = {
                    "$match" : {
                        # "inventory_docs.site_type": {"$regex" : re.compile(channel, re.IGNORECASE)},
                        "inventory_docs.content": {"$regex" : re.compile(search, re.IGNORECASE)}
                    }
                }

        if search == "null" or len(search) < 1:
            pass
        else:
            query["content"] = {"$regex" : re.compile(search, re.IGNORECASE)}
        

        if limit is None:
            limit = 10
        else:
            limit = int(limit)

        if page:
            page = int(page)
            index = int(limit) * int(page - 1)
        else:
            index = 0

        ignore = {
            "Doc_id":0,
            "twitter_retweeted_status_author_location":0,
            "twitter_retweeted_status_author_location_city":0,
            "title_norm":0,
            "content_parsed":0,
            "channel":0,
            "title_noun":0,
            "location_longitude":0,
            "twitter_retweeted_status_author_demographics":0,
            "content_norm":0,
            "twitter_retweeted_status_author_demographics_family_status":0,
            "twitter_retweeted_status_author_demographics_job_list":0,
            "twitter_retweeted_status_author_url":0,
            "content_lemmatized":0,
            "ratings_raw":0,
            "title_parsed":0,
            "twitter_retweeted_status_sentiment":0,
            "title_pre_processed":0,
            "synthesio_rank":0,
            "title_lemmatized":0,
            "crawled_at":0,
            "sentiment":0,
            "site_id":0,
            "location_latitude":0,
            "twitter_retweeted_status_author_location_country":0,
            "twitter_retweeted_status_title":0,
            "twitter_retweeted_status_date":0,
            "twitter_retweeted_status_author_demographics_affinity_list":0,
            "location":0,
            "location_country":0,
            "_id":0,
            # "date":0,
            "human_review_status":0,
            "twitter_retweeted_status_author_demographics_gender":0,
            "language":0,
            "twitter_retweeted_status_author_demographics_marital_status":0,
            "content_noun_adj":0,
            "twitter_retweeted_status_author_demographics_bio_tag_list":0,
            "site_name":0,
            "all-in-one":0,
            "ratings_normalized":0,
            "twitter_retweeted_status_author_location_latitude":0,
            "content_noun":0,
            "twitter_retweeted_status_author_picture_url":0,
            "twitter_retweeted_status_author_location_state":0,
            "title_noun_adj":0,
            "twitter_retweeted_status_author_demographics_age":0,
            "content_pre_processed":0,
            "twitter_retweeted_status_author_location_longitude":0,
            "twitter_retweeted_status_author_location_county":0,
            "twitter_retweeted_status_url":0
        }


        api = {
                "category":category,
                "limit": limit,
                "page": page,
                "has_more": None,
                "data" : []
            }
        
        if needstate and keyword:
            ns_kw_filter = {
                "$match": {
                    "NS": needstate,
                    "KW": {"$in": keyword.split(",")} ,
                    "Sentiment" : { "$gte":  gt, "$lte": lt },
                }
            }
        elif needstate:
            ns_kw_filter = {
                            "$match": {
                                "NS": needstate,
                                "Sentiment" : { "$gt":  gt, "$lte": lt }
                            }
                        }
        else:
            ns_kw_filter = {
                "$match": {
                    "Sentiment" : { "$gt":  gt, "$lte": lt }
                }
            }



        if channel and channel != 'all':
            ns_kw_filter['$match']['Channel'] = channel
        
        if needstate is not None:
            if lookup_match:
                data = mycol2.aggregate([
                            ns_kw_filter,
                            {"$group" : 
                                {"_id" : {"docgroupid": "$doc_id"},
                                        "totalS": { "$avg": "$Sentiment" }
                                    }
                                },                            
                            
                            
                            {
                                "$lookup": {
                                    "from": join,
                                    "localField": "_id.docgroupid",
                                    "foreignField": "doc_id",
                                    "as": "inventory_docs"
                                }
                            },
                            {
                                "$unwind": "$inventory_docs"
                            },
                            lookup_match,
                            {
                                "$project": {
                                "inventory_docs.title": 1,
                                "inventory_docs.content": 1,
                                "inventory_docs.date": 1,
                                "inventory_docs.url": 1,
                                "inventory_docs.site_type": 1,
                                "totalS": 1,
                                }
                            },
                            {"$sort":{'totalS':sflag}},
                            { "$skip" : index },
                            { "$limit": limit },
                    ])
                res = json.loads(dumps(data))  
            else:
                data = mycol2.aggregate([
                            ns_kw_filter,
                            {"$group" : {"_id" : {"docgroupid": "$doc_id"},"totalS": { "$avg": "$Sentiment" }}},
                            
                            {"$sort":{'totalS':sflag}},
                            { "$skip" : index },
                            { "$limit": limit },
                            {
                                "$lookup": {
                                    "from": join,
                                    "localField": "_id.docgroupid",
                                    "foreignField": "doc_id",
                                    "as": "inventory_docs"
                                }
                            },
                            {
                                "$unwind": "$inventory_docs"
                            },
                            {
                                "$project": {
                                "inventory_docs.title": 1,
                                "inventory_docs.content": 1,
                                "inventory_docs.date": 1,
                                "inventory_docs.url": 1,
                                "inventory_docs.site_type": 1,
                                "totalS": 1,
                                }
                            }
                    ])
                res = json.loads(dumps(data))
        else:
            # data = mycol.find(query, ignore).skip(index).limit(limit)
            
            if lookup_match:
                data = mycol2.aggregate([
                            ns_kw_filter,
                            {"$group" : {"_id" : {"docgroupid": "$doc_id"},"totalS": { "$avg": "$Sentiment" }}},
                            
                            
                            {
                                "$lookup": {
                                    "from": join,
                                    "localField": "_id.docgroupid",
                                    "foreignField": "doc_id",
                                    "as": "inventory_docs"
                                }
                            },
                            {
                                "$unwind": "$inventory_docs"
                            },
                            lookup_match,   
                            {
                                "$project": {
                                "inventory_docs.title": 1,
                                "inventory_docs.content": 1,
                                "inventory_docs.date": 1,
                                "inventory_docs.url": 1,
                                "inventory_docs.site_type": 1,
                                "totalS": 1,
                                }
                            },
                            {"$sort":{'totalS':sflag}},
                            { "$skip" : index },
                            { "$limit": limit },
                    ])
            else:
                
                data = mycol2.aggregate([
                        ns_kw_filter,
                        {"$group" : {"_id" : {"docgroupid": "$doc_id"},"totalS": { "$avg": "$Sentiment" }}},
                        
                        {"$sort":{'totalS':sflag}},
                        { "$skip" : index },
                        { "$limit": limit },
                        {
                            "$lookup": {
                                "from": join,
                                "localField": "_id.docgroupid",
                                "foreignField": "doc_id",
                                "as": "inventory_docs"
                            }
                        },
                        {
                            "$unwind": "$inventory_docs"
                        },
                        {
                            "$project": {
                            "inventory_docs.title": 1,
                            "inventory_docs.content": 1,
                            "inventory_docs.date": 1,
                            "inventory_docs.url": 1,
                            "inventory_docs.site_type": 1,
                            "totalS": 1,
                            }
                        }
                ])
            res = json.loads(dumps(data))
 
        # check has more
        # has = mycol.find(query, ignore).skip(index + limit + 1).limit(limit)
        # more = json.loads(dumps(has))

        # if len(more) > 0:
        #     api['has_more'] = True
        # else:
        api['has_more'] = True

        # if needstate is not None:
        new_res = []
        for i in res:
            new_res.append(i['inventory_docs'])
            i['inventory_docs']['totalS'] = i['totalS']
        new_res=sorted(new_res,key=lambda i:(i['totalS'],i['date'], i['site_type']))
        counter = 0
        for i in new_res:
            i['id'] = counter+1
            counter+=1
        api['data'] = new_res
        # else:
        #     res=sorted(res,key=lambda i:(i['date'], i['site_type']))
        #     api['data'] = res
        
        return api

    # database logic for categoryview -> emerging_needstates

    def emerging_needstates(request):
        category      = request.GET.get('category')
        channel       = request.GET.get('channel')
        country       = request.GET.get('country')
        
        if category is None:
            return {"code":400, "msg":"category Required"}
        if country is None:
            return {"code":400, "msg":"country Required"}
        if channel is None:
            return {"code":400, "msg":"channel Required"}

        mydb   = myclient[category]
        mycol  = mydb[Cname_LS1 + country]
        mycol2  = mydb[Cname_EugenieTable + country]  
        mycol3= mydb[Cname_LS2 + country]        
       
        if channel=="all":
            channelEmerg="all"
        else:
            channelEmerg=channel.replace("_","")

                   
        
        lsdates= mycol.find({"channel":channelEmerg}).distinct('latest_date')
        lsdates=json.loads(dumps(lsdates))
        lsdates.sort()
        lsdates=lsdates[-6:]

        need={"_id":0,"latest_date":1,"emerging_needstates":1}

        qu = mycol.find({"channel":channelEmerg,"latest_date":{"$in":lsdates}},need)
        x=json.loads(dumps(qu))

        need2={"_id":0,"latest_date":1,"viral_needstates":1}
        quviral = mycol3.find({"channel":channelEmerg,"latest_date":{"$in":lsdates}},need2)
        x2=json.loads(dumps(quviral))
        

        nsList=json.loads(dumps(mycol2.find().distinct('Need state')))

      
        res=[]

        for i in nsList:
            temp=[]
            for j in lsdates:
                tempSub=[k for k in x if k['latest_date']==j]
                
                emerging_NS_pos=[]
                emerging_NS_neg=[]
                try:
                    if tempSub[0]['emerging_needstates']:
                        emerging_NS=list(tempSub[0]['emerging_needstates'].keys())
                        for l in emerging_NS:
                            if tempSub[0]['emerging_needstates'][l][0][2]=="Positive":
                                emerging_NS_pos.append(l)
                            else:
                                emerging_NS_neg.append(l)
                except KeyError:
                    pass

                
                classi='stable'
                if i in emerging_NS_neg:
                    classi='decline'
                if i in emerging_NS_pos:
                    classi='emerging'

                temp.append(classi)
                
            res.append({'NS':i,'data':temp})

        viralclass=[k for k in x2 if k['latest_date']==lsdates[-1]][0]['viral_needstates']


        for i in res:
            t=i['data']
            cntrank=t.count(t[-1])
            y=[i==t[-1] for i in t ]
            try:
                recencyrank=(len(y)-(max([i for i,j in enumerate(y) if j==False])+1))
            except:
                recencyrank=len(y)

            if recencyrank==1:
                i['prev']='Shift in Lifestage \nPrevious lifestage - '+t[-2]
                i['strokeClr']='red'
                i['strokeWidth']=2
            else:
                i['prev']=""
                i['strokeClr']='black'
                i['strokeWidth']=1

            if( t[-1]=="emerging") & (i['NS'] in viralclass):
                i['strokeClr']='red'
                i['prev']='Viral emerging'


            i['recency_rank']=recencyrank
            i['count_rank']=cntrank 
            i['class']=t[-1]    
            i['cumrank']=recencyrank+cntrank          

         

        ld = mycol2.find().sort('Date', -1).limit(1)
        rd = json.loads(dumps(ld, indent=2))
        latest_date_str =rd[0]['Date']
        latest_date = datetime.strptime(latest_date_str, '%Y-%m-%d')

        today       = latest_date

        six_month   = relativedelta(months=6)
        six_months_back_date    = today - six_month
        
        today = str(today.isoformat())
        six_months_back_date = str(six_months_back_date.isoformat())

        if channel=="all":
            AbsM="$Abs"
            DocM="$DocCount"
        else:
            AbsM="$Abs_"+channelEmerg
            DocM="$DocCount_"+channelEmerg

        group = {
                "$group" : {
                        "_id" : "$Need state",
                         "total_abs": { "$sum" : AbsM },
                         "total_doc": { "$sum" : DocM },
                         
                    }
                }
        projectnull = {
                 '$project': {
                        '_id': 1,
                        'total_abs': { '$ifNull': [ "$total_abs", 0 ] },
                        'total_doc': { '$ifNull': [ "$total_doc", 0 ] },
                        
                            }
                    }

        query_for_today_to_last_three_months = mycol2.aggregate([
            {
                "$match": {
                    'Keyword' : None,
                    "Date": { "$gte":  six_months_back_date, "$lt": today }
                }
            },
            group,
            projectnull
        ])

        cintensity=json.loads(dumps(query_for_today_to_last_three_months))

        
        resfinal=[]
        for i in res:
            val=[m for m in cintensity if m['_id']==i['NS']]
            val=val[0]['total_abs']/val[0]['total_doc']

            if i['class']=='stable':
                resfinal.append({'NS': i['NS'], 'valueyaxis':val , 'valueStable': i['cumrank'],"prev":i['prev'],'strokeClr':i['strokeClr'],'strokeWidth':i['strokeWidth']})
            if i['class']=='decline':
                resfinal.append({'NS': i['NS'], 'valueyaxis':val , 'valueDecline': i['cumrank'],"prev":i['prev'],'strokeClr':i['strokeClr'],'strokeWidth':i['strokeWidth']})
            if i['class']=='emerging':
                resfinal.append({'NS': i['NS'], 'valueyaxis':val , 'valueEmerging': i['cumrank'],"prev":i['prev'],'strokeClr':i['strokeClr'],'strokeWidth':i['strokeWidth']})
   
        api={
            "data" : []
        }
        api['data']=resfinal

        return api
    # database logic for categoryview -> top_needstate

    def top_needstates(request):
        category      = request.GET.get('category')
        abs           = request.GET.get('abs')
        channel       = request.GET.get('channel')
        country       = request.GET.get('country')
        metric        = request.GET.get('metric')

        if category is None:
            return {"code":400, "msg":"category Required"}
        if country is None:
            return {"code":400, "msg":"country Required"}
        if channel is None:
            return {"code":400, "msg":"channel Required"}

        mydb   = myclient[category]
        mycol  = mydb[Cname_EugenieTable + country]
        mycol2 = mydb[Cname_NeedstateTable + country]

        
        if abs is None:
            return {"code":400, "msg":"abs Required"}
        else:
            if abs == 'Abs':
                AbsM = "$"+metric
            else:
                AbsM = "$"+metric+abs

        if channel=="all":
            channelEmerg="all"
        else:
            channelEmerg=channel.replace("_","")

                # TO BE DELETED LATER
        # if (category == "Surface_care" and country == "IND"):
        #     if channel == 'all':
        #         channelEmerg="Abs"
        #     else:
        #         channelEmerg = "Abs"+channelEmerg
        
        qu = mycol2.find({"channel":channelEmerg})
        x=json.loads(dumps(qu))
        lsdates= mycol2.find({"channel":channelEmerg}).distinct('latest_date')
        lsdates=json.loads(dumps(lsdates))
        lsdates.sort()
        lsdates=lsdates[-1]
        x=[i for i in x if i['latest_date']==lsdates]

        if x:
            emerging_NS=list(x[0]['emerging_needstates'].keys())
            emerging_NS_pos=[]
            emerging_NS_neg=[]
            for i in emerging_NS:
                if x[0]['emerging_needstates'][i][0][2]=="Positive":
                    emerging_NS_pos.append(i)
                else:
                    emerging_NS_neg.append(i)

        ld = mycol.find().sort('Date', -1).limit(1)
        rd = json.loads(dumps(ld, indent=2))
        latest_date_str =rd[0]['Date']
        latest_date = datetime.strptime(latest_date_str, '%Y-%m-%d')

        today       = latest_date


        # today       = datetime.today()
        three_month = relativedelta(months=3)
        six_month   = relativedelta(months=6)
        one_year    = relativedelta(months=12)
        two_year    =relativedelta(months=24)

        three_months_back_date  = today - three_month
        six_months_back_date    = today - six_month
        one_year_back_date      = today - one_year

        three_months_back_date_from_three_month = today - three_month - three_month
        six_months_back_date_from_six_months    = today - six_month - six_month
        one_year_back_date_from_one_year        = today - one_year - one_year

        today = str(today.isoformat())
        three_months_back_date = str(three_months_back_date.isoformat())
        six_months_back_date = str(six_months_back_date.isoformat())
        one_year_back_date = str(one_year_back_date.isoformat())
        three_months_back_date_from_three_month = str(three_months_back_date_from_three_month.isoformat())
        six_months_back_date_from_six_months = str(six_months_back_date_from_six_months.isoformat())
        one_year_back_date_from_one_year = str(one_year_back_date_from_one_year.isoformat())

        if metric=='Abs':
            group = {
                "$group" : {
                        "_id" : "$Need state", "total_abs": { "$sum" : AbsM }
                    }
                }
        else:
            group = {
                "$group" : {
                        "_id" : "$Need state", "total_abs": { "$avg" : AbsM }
                    }
                }
        projectnull = {
                 '$project': {
                        '_id': 1,
                        'total_abs': { '$ifNull': [ "$total_abs", 0 ] }
                            }
                    }

        query_for_today_to_last_three_months = mycol.aggregate([
            {
                "$match": {
                    'Keyword' : None,
                    "Date": { "$gte":  three_months_back_date, "$lt": today }
                }
            },
            group,
            projectnull
        ])



        # end query

        query_for_last_three_months_to_next_three_months = mycol.aggregate([
            # mongo_date_formatter,
            {
                "$match": {
                    'Keyword' : None,
                    "Date": { "$gte": three_months_back_date_from_three_month, "$lt": three_months_back_date }
                }
            },
            group,
            projectnull
        ])


        #query end

        query_for_today_to_last_six_months = mycol.aggregate([
            # mongo_date_formatter,
            {
                "$match": {
                    'Keyword' : None,
                    "Date": { "$gte": six_months_back_date, "$lt": today }
                }
            },
            group,
            projectnull
        ])


        #query end
        query_for_last_six_months_to_next_six_months = mycol.aggregate([
            # mongo_date_formatter,
            {
                "$match": {
                    'Keyword' : None,
                    "Date": { "$gte": six_months_back_date_from_six_months, "$lt": six_months_back_date }
                }
            },
            group,
            projectnull
        ])


        #query end

        query_for_today_to_last_one_year = mycol.aggregate([
            # mongo_date_formatter,
            {
                "$match": {
                    'Keyword' : None,
                    "Date": { "$gte": one_year_back_date, "$lt": today }
                }
            },
            group,
            projectnull
        ])

        #query end

        query_for_last_one_year_to_next_one_year = mycol.aggregate([
            # mongo_date_formatter,
            {
                "$match": {
                    'Keyword' : None,
                    "Date": { "$gte": one_year_back_date_from_one_year, "$lt": one_year_back_date }
                }
            },
            group,
            projectnull
        ])

        res_for_today_to_last_three_months             = json.loads(dumps(query_for_today_to_last_three_months))
        res_for_last_three_months_to_next_three_months = json.loads(dumps(query_for_last_three_months_to_next_three_months))
        res_for_today_to_last_six_months               = json.loads(dumps(query_for_today_to_last_six_months))
        res_for_last_six_months_to_next_six_months     = json.loads(dumps(query_for_last_six_months_to_next_six_months))
        res_for_today_to_last_one_year                 = json.loads(dumps(query_for_today_to_last_one_year))
        res_for_last_one_year_to_next_one_year         = json.loads(dumps(query_for_last_one_year_to_next_one_year))

        api = {
            "category" : category,
            "three_month" : [],
            "six_month"   : [],
            "one_year"    : []
        }

  

        res_for_today_to_last_three_months = [{'_id':ele['_id'],'total':[ele['total_abs'],ele1['total_abs']]} for ele in res_for_today_to_last_three_months for ele1 in res_for_last_three_months_to_next_three_months if ele['_id']==ele1['_id']]
        res_for_today_to_last_six_months = [{'_id':ele['_id'],'total':[ele['total_abs'],ele1['total_abs']]} for ele in res_for_today_to_last_six_months for ele1 in res_for_last_six_months_to_next_six_months if ele['_id']==ele1['_id']]
        res_for_today_to_last_one_year = [{'_id':ele['_id'],'total':[ele['total_abs'],ele1['total_abs']]} for ele in res_for_today_to_last_one_year for ele1 in res_for_last_one_year_to_next_one_year if ele['_id']==ele1['_id']]

        # res_for_today_to_last_three_months = [ {'_id':i['_id'],'total':[i['total_abs'],j['total_abs']]} for i,j in zip(res_for_today_to_last_three_months, res_for_last_three_months_to_next_three_months)]
        # res_for_today_to_last_six_months   = [ {'_id':i['_id'],'total':[i['total_abs'],j['total_abs']]} for i,j in zip(res_for_today_to_last_six_months, res_for_last_six_months_to_next_six_months)]
        # res_for_today_to_last_one_year     = [ {'_id':i['_id'],'total':[i['total_abs'],j['total_abs']]} for i,j in zip(res_for_today_to_last_one_year, res_for_last_one_year_to_next_one_year)]


        three_month = res_for_today_to_last_three_months
        if len(three_month) > 0:
            for i in three_month:
                # if i['total'][0] == 0:
                #     i['total'][0] = 0
                if (i['total'][1] == 0 and i['total'][0] == 0 ):
                    i['percentage'] = int(0)
                elif i['total'][1] == 0 :
                    i['percentage'] = -99999
                else:
                    i['percentage'] = int((i['total'][0]/i['total'][1]-1)*100)
                i["total_abs"] = round(sum(i['total']),3)
            for i in three_month:del i["total"]

        six_month = res_for_today_to_last_six_months

        if len(six_month) > 0:
            for i in six_month:
                # if i['total'][0] == 0:
                #     i['total'][0] = 1
                if (i['total'][1] == 0 and i['total'][0] == 0 ):
                    i['percentage'] = int(0)
                elif i['total'][1] == 0 :
                    i['percentage'] = -99999
                else:
                    i['percentage'] = int((i['total'][0]/i['total'][1]-1)*100)
                i["total_abs"] = round(sum(i['total']), 3)
            for i in six_month:del i["total"]

        one_year = res_for_today_to_last_one_year
        if len(one_year) > 0:
            for i in one_year:
                if (i['total'][1] == 0 and i['total'][0] == 0 ):
                    i['percentage'] = int(0)
                elif i['total'][1] == 0 :
                    i['percentage'] = -99999
                else:
                    i['percentage'] = int((i['total'][0]/i['total'][1]-1)*100)
                i["total_abs"] = round(sum(i['total']),3)
            for i in one_year:del i["total"]

        if one_year:
            for i in one_year:
                i['needstate'] = i['_id']
                i['one_year_percentage'] = i['percentage']
                i['one_year_abs'] = i['total_abs']
                del i['percentage']
                del i['total_abs']
                del i['_id']

        if three_month:
            for i in three_month:
                    i['needstate'] = i['_id']
                    i['three_month_percentage'] = i['percentage']
                    i['three_month_abs'] = i['total_abs']
                    del i['total_abs']
                    del i['percentage']
                    del i['_id']

        if six_month:
            for i in six_month:
                    i['needstate'] = i['_id']
                    i['six_month_percentage'] = i['percentage']
                    i['six_month_abs'] = i['total_abs']
                    del i['total_abs']
                    del i['percentage']
                    del i['_id']

        one = dict_merger(coln=['one_year_percentage','one_year_abs'], collection_=one_year, colle_to_update=six_month, key_col='needstate')
        two = dict_merger(coln=['three_month_percentage','three_month_abs'], collection_=three_month, colle_to_update=one, key_col='needstate')

        if x:
            for t in two:
                if t['needstate'] in emerging_NS_pos:
                    t['is_emerging'] = "a"
                elif t['needstate'] in emerging_NS_neg:
                    t['is_emerging'] = "d"
                else:
                    t['is_emerging'] = "n"

        for i in two:
            if "three_month_percentage" not in i:
                i['three_month_percentage'] = 0
        if x:
            try:
                two=sorted(two,key=lambda i:(i['is_emerging'],-i['six_month_percentage']))
            except KeyError:
                pass
        else:
            two=sorted(two,key=lambda i:(-i['six_month_percentage']))

        for i in two:
            if i['three_month_percentage']==-99999:
                i['three_month_percentage']='inf'
            if i['six_month_percentage']==-99999:
                i['six_month_percentage']='inf'
            if i['one_year_percentage']==-99999:
                i['one_year_percentage']='inf'


        return two
    
    def summary_table(request):
        category      = request.GET.get('category')
        abs           = request.GET.get('abs')
        channel       = request.GET.get('channel')
        country       = request.GET.get('country')
        metric        = request.GET.get('metric')

        top_needstates = CategoryView.top_needstates(request)

        if top_needstates:

            # top_needstates=sorted(top_needstates,key=lambda i:(-i['six_month_percentage']))
            # cnt=0
            # for i in top_needstates:
            #     i['r1']=cnt
            #     cnt=cnt+1
            top_needstates=sorted(top_needstates,key=lambda i:(-i['six_month_abs']))
            # cnt=0
            # for i in top_needstates:
            #     i['r2']=cnt
            #     cnt=cnt+1
            # for i in top_needstates:
            #     i['r3']=i['r1']+i['r2']
            
            # top_needstates=sorted(top_needstates,key=lambda i:(-i['r3']))
            # top_needstates = top_needstates[7:]

        for i in top_needstates:
            
            del i['one_year_percentage']
            del i['one_year_abs']
            del i['three_month_percentage']
            del i['three_month_abs']

        for i in top_needstates:
            sentiments = CategoryView.keyword_level_sentiment(request, i['needstate'])
            if sentiments:
                del sentiments[0]['year']
                i["sentiment"] = sentiments[0]
            
            
            high = []
            low = []
            medium = []

            brand_health = Utils.brand_split_chart(request, i['needstate'])
            brand_health = [i for i in brand_health if i['perc'] > 4.9 and i["brand"] != "others"]

            for b in brand_health:
                t=b['t_P']/(b['t_P']+b['t_N']+b['t_Neg'])
                if t > .6666:
                    high.append(b['brand'])
                elif t > .3333:
                    medium.append(b['brand'])
                else:
                    low.append(b['brand'])

                
            i["brand_health"] = {"high": high, "medium": medium, "low": low}
            # try:
            #     trending_topics = Utils.top_keywords(request, i['needstate'])[:3]
            # except IndexError:
            #     trending_topics = []

            asso_needstates = []
            try:
                associated_needstate = Utils.association_chart_limited(request, i['needstate'])
            except:
                associated_needstate=[]
            
            tp = []
            asn=[]
            for j in associated_needstate:
                tp.append(j['value'])
                asn.append(j['key'])

            seen_asn = set()
            asn_out=[x for x in asn if x not in seen_asn and not seen_asn.add(x)]
            seen_tp = set()
            tp_out=[x for x in tp if x not in seen_tp and not seen_tp.add(x)]

            i["oppourtinity_lens"] = {
                    "associated_needstate":asn_out[:3],
                    "trending_topics":tp_out[:5]
                }
 
        top_needstates=sorted(top_needstates,key=lambda i:(-i['six_month_abs']))
        for i in top_needstates:
            i['needstate']= i['needstate'].replace("/","") 

        return top_needstates

    # database logic for categoryview -> share_of_voice_as_per_geography
    def share_of_voice_as_per_geography(request):

        category  = request.GET.get('category')
        group     = request.GET.get('group')
        channel     = request.GET.get('channel')
        date      = request.GET.get('date')
        needstate = request.GET.get('needstate')
        country   = request.GET.get('country')

        if category is None:
            return {"code":400, "msg":"category Required"}

        if date is None:
            return {"code":400, "msg":"date Required"}


        if channel == "all":
            abs_channel = "$Abs"
        else:
            abs_channel = "$Abs"+channel
            

        api = {}

        try:    
            api['us'] = CategoryView.funcGen('USA',channel,needstate,category,abs_channel)['chatter_volume']
        except KeyError:
            api['us'] = 0

        try:
            api['uk'] = CategoryView.funcGen('GBR',channel,needstate,category,abs_channel)['chatter_volume']
        except KeyError:
            api['uk'] = 0
        try:
            api['india'] = CategoryView.funcGen('IND',channel,needstate,category,abs_channel)['chatter_volume']
        except KeyError:
            api['india'] = 0


        if api["us"] == 0:
            api["us_color"] = "lightgrey"
        else:
            api["us_color"] = "blue"

        if api["uk"] == 0:
            api["uk_color"] = "lightgrey"
        else:
            api["uk_color"] = "red"

        if api["india"] == 0:
            api["india_color"] = "lightgrey"
        else:
            api["india_color"] = "lightgreen"


        return api

    # database logic for categoryview -> top_keywords
    def top_keywords(request):
        category          = request.GET.get('category')
        channel = request.GET.get('channel')
        country = request.GET.get('country')
        needstate = request.GET.get('needstate')
        metric=  request.GET.get('metric')

        mydb   = myclient[category]
        mycol  = mydb[Cname_EugenieTable + country]
        mycol2 = mydb[Cname_NeedstateTable + country]

        if needstate is None:
            return {"code":400, "msg":"needstate Required"}


        if channel=="all":
            channelEmerg="all"
            AbsM="$"+metric
        else: 
            channelEmerg=channel.replace("_","")
            AbsM="$"+metric+channel
        
        #         # TO BE DELETED LATER
        # if (category == "Surface_care" and country == "IND"):
        #     if channel == 'all':
        #         channelEmerg="Abs"
        #     else:
        #         channelEmerg = "Abs"+channelEmerg

        qu = mycol2.find({"channel":channelEmerg})
        qu.batch_size(50000)
        x=json.loads(dumps(qu))
        qu.close()
        lsdates= mycol2.find({"channel":channelEmerg}).distinct('latest_date')
        lsdates=json.loads(dumps(lsdates))
        lsdates.sort()
        lsdates=lsdates[-1]
        x=[i for i in x if i['latest_date']==lsdates]

        driving_keyword = []

        try:
            emerging_needstates = x[0]['emerging_needstates'][needstate][1]['emerging_keywords']
            driving_keyword = [{e[1]:e[3]} for e in emerging_needstates]
        except KeyError:
            pass

        try:
            emerging_parent_keywords = x[0]['emerging_parent_keywords']
            if emerging_parent_keywords:
                for i in emerging_parent_keywords:
                    driving_keyword.append({i[0]:i[3]})
        except KeyError:
            pass

        ld = mycol.find().sort('Date', -1).limit(1)
        rd = json.loads(dumps(ld, indent=2))
        latest_date_str =rd[0]['Date']
        latest_date = datetime.strptime(latest_date_str, '%Y-%m-%d')
        today       = latest_date


        three_month = relativedelta(months=3)
        six_month   = relativedelta(months=6)
        one_year    = relativedelta(months=12)
        two_year    = relativedelta(months=24)
        

        three_months_back_date  = today - three_month
        six_months_back_date    = today - six_month
        one_year_back_date      = today - one_year

        three_months_back_date_from_three_month = today - three_month - three_month
        six_months_back_date_from_six_months    = today - six_month - six_month
        one_year_back_date_from_one_year        = today - one_year - six_month

        today = str(today.isoformat())
        three_months_back_date = str(three_months_back_date.isoformat())
        six_months_back_date = str(six_months_back_date.isoformat())
        one_year_back_date = str(one_year_back_date.isoformat())
        three_months_back_date_from_three_month = str(three_months_back_date_from_three_month.isoformat())
        six_months_back_date_from_six_months = str(six_months_back_date_from_six_months.isoformat())
        one_year_back_date_from_one_year = str(one_year_back_date_from_one_year.isoformat())

        projectnull = {
                 '$project': {
                        '_id': 1,
                        'total_abs': { '$ifNull': [ "$total_abs", 0 ] }
                            }
                    }

        if metric=='Abs':
            group = {
                "$group" : {
                        "_id" : "$Keyword", "total_abs": { "$sum" : AbsM }
                    }
                }
        else:
            group = {
                "$group" : {
                        "_id" : "$Keyword", "total_abs": { "$avg" : AbsM }
                    }
                }

        # mongo_date_formatter = {
        #     "$addFields": {
        #         "Date": {
        #             "$dateFromString": {
        #                 "dateString": "$Date",
        #                 "format": "%d/%m/%Y"
        #             }
        #         }
        #     }
        # }

        query_for_today_to_last_three_months = mycol.aggregate([
            # mongo_date_formatter,
            {
                "$match": {
                    'Keyword' : {"$ne" : None},
                    'Need state': needstate,
                    "Date": { "$gte": three_months_back_date, "$lt": today }
                }
            },
            group,
            projectnull
        ])
        query_for_today_to_last_three_months.batch_size(50000)

        query_for_last_three_months_to_next_three_months = mycol.aggregate([
            # mongo_date_formatter,
            {
                "$match": {
                    'Keyword' : {"$ne" : None},
                    'Need state': needstate,
                    "Date": { "$gte": three_months_back_date_from_three_month, "$lt": three_months_back_date }
                }
            },
            group,
            projectnull
        ])
        query_for_last_three_months_to_next_three_months.batch_size(50000)

        query_for_today_to_last_six_months = mycol.aggregate([
            # mongo_date_formatter,
            {
                "$match": {
                    'Keyword' : {"$ne" : None},
                    'Need state': needstate,
                    "Date": { "$gte": six_months_back_date, "$lt": today }
                }
            },
            group,
            projectnull
        ])
        query_for_today_to_last_six_months.batch_size(50000)

        query_for_last_six_months_to_next_six_months = mycol.aggregate([
            # mongo_date_formatter,
            {
                "$match": {
                    'Keyword' : {"$ne" : None},
                    'Need state': needstate,
                    "Date": { "$gte": six_months_back_date_from_six_months, "$lt": six_months_back_date }
                }
            },
            group,
            projectnull
        ])
        query_for_last_six_months_to_next_six_months.batch_size(50000)

        query_for_today_to_last_one_year = mycol.aggregate([
            # mongo_date_formatter,
            {
                "$match": {
                    'Keyword' : {"$ne" : None},
                    'Need state': needstate,
                    "Date": { "$gte": one_year_back_date, "$lt": today }
                }
            },
            group,
            projectnull
        ])
        query_for_today_to_last_one_year.batch_size(50000)

        query_for_last_one_year_to_next_one_year = mycol.aggregate([
            # mongo_date_formatter,
            {
                "$match": {
                    'Keyword' : {"$ne" : None},
                    'Need state': needstate,
                    "Date": { "$gte": one_year_back_date_from_one_year, "$lt": one_year_back_date }
                }
            },
            group,
            projectnull
        ])
        query_for_last_one_year_to_next_one_year.batch_size(50000)



        res_for_today_to_last_three_months             = json.loads(dumps(query_for_today_to_last_three_months))
        res_for_last_three_months_to_next_three_months = json.loads(dumps(query_for_last_three_months_to_next_three_months))
        res_for_today_to_last_six_months               = json.loads(dumps(query_for_today_to_last_six_months))
        res_for_last_six_months_to_next_six_months     = json.loads(dumps(query_for_last_six_months_to_next_six_months))
        res_for_today_to_last_one_year                 = json.loads(dumps(query_for_today_to_last_one_year))
        res_for_last_one_year_to_next_one_year         = json.loads(dumps(query_for_last_one_year_to_next_one_year))

        query_for_today_to_last_three_months.close()
        query_for_last_three_months_to_next_three_months.close()
        query_for_today_to_last_six_months.close()
        query_for_last_six_months_to_next_six_months.close()
        query_for_today_to_last_one_year.close()
        query_for_last_one_year_to_next_one_year.close()

        api = {
            "category" : category,
            "three_month" : [],
            "six_month"   : [],
            "one_year"    : []
        }


        res_for_today_to_last_three_months = [{'_id':ele['_id'],'total':[ele['total_abs'],ele1['total_abs']]} for ele in res_for_today_to_last_three_months for ele1 in res_for_last_three_months_to_next_three_months if ele['_id']==ele1['_id']]
        res_for_today_to_last_six_months = [{'_id':ele['_id'],'total':[ele['total_abs'],ele1['total_abs']]} for ele in res_for_today_to_last_six_months for ele1 in res_for_last_six_months_to_next_six_months if ele['_id']==ele1['_id']]
        res_for_today_to_last_one_year = [{'_id':ele['_id'],'total':[ele['total_abs'],ele1['total_abs']]} for ele in res_for_today_to_last_one_year for ele1 in res_for_last_one_year_to_next_one_year if ele['_id']==ele1['_id']]


        three_month = res_for_today_to_last_three_months
        if len(three_month) > 0:
            for i in three_month:
                # if i['total'][0] == 0:
                #     i['total'][0] = 0
                if (i['total'][1] == 0 and i['total'][0] == 0 ):
                    i['percentage'] = int(0)
                elif i['total'][1] == 0 :
                    i['percentage'] = -99999
                else:
                    i['percentage'] = int((i['total'][0]/i['total'][1]-1)*100)
            for i in three_month:del i["total"]

        six_month = res_for_today_to_last_six_months
        if len(six_month) > 0:
            for i in six_month:
                # if i['total'][0] == 0:
                if (i['total'][1] == 0 and i['total'][0] == 0 ):
                    i['percentage'] = int(0)
                elif i['total'][1] == 0 :
                    i['percentage'] = -99999
                else:
                    i['percentage'] = int((i['total'][0]/i['total'][1]-1)*100)
            for i in six_month:del i["total"]

        one_year = res_for_today_to_last_one_year
        if len(one_year) > 0:
            for i in one_year:
                if (i['total'][1] == 0 and i['total'][0] == 0 ):
                    i['percentage'] = int(0)
                elif i['total'][1] == 0 :
                    i['percentage'] = -99999
                else:
                    i['percentage'] = int((i['total'][0]/i['total'][1]-1)*100)
            for i in one_year:del i["total"]

        
        for i in three_month:
            i['needstate'] = i["_id"]
            i['three_month_percentage'] = i['percentage']
            del i["_id"]
        for i in six_month:
            i['six_month_percentage'] = i['percentage']
            i['needstate'] = i["_id"]
            del i["_id"]
        for i in one_year:
            i['one_year_percentage'] = i['percentage']
            i['needstate'] = i["_id"]
            del i["_id"]

        

        # api["three_month"] = three_month
        # api["six_month"]   = six_month
        # api["one_year"]    = one_year


        one = dict_merger2(coln='one_year_percentage', collection_=one_year, colle_to_update=six_month, key_col='needstate')
        two = dict_merger2(coln='three_month_percentage', collection_=three_month, colle_to_update=one, key_col='needstate')



        for i in two:
            del i['percentage']

        # for i in two:
        #     if i['needstate'] in { k:i for i,k in enumerate(driving_keyword)}.keys():
        #         print("yes")
        #     else:
        #         print("No")

        # for i in two:
        #     for j in driving_keyword:
        #         if i['needstate'] in j.keys() and 'Negative' in j.values():
        #             i['driving'] = False
        #         elif i['needstate'] in j.keys() and 'Positive' in j.values():
        #              i['driving'] = True
        #         else:
        #             i['driving'] = None

        if driving_keyword:
            for i in two:
                for j in driving_keyword:
                    if i['needstate'] in j.keys() and 'Negative' in j.values():
                        i['driving'] = "d"
                        break
                    elif i['needstate'] in j.keys() and 'Positive' in j.values():
                        i['driving'] = "a"
                        break
                    else:
                        i['driving'] = "n"
                        
        else:
            for i in two:
                i['driving'] = "n"
       
        for i in two:
            if "three_month_percentage" not in i:
                i['three_month_percentage'] = 0
                
        if x:
            try:
                two=sorted(two, key=lambda i:(i['driving'], -i['six_month_percentage']))
            except KeyError:   
                pass    
        else:
            two=sorted(two,key=lambda i:(-i['six_month_percentage']))

        for i in two:
            if i['three_month_percentage']==-99999:
                i['three_month_percentage']='inf'
            if i['six_month_percentage']==-99999:
                i['six_month_percentage']='inf'
            if i['one_year_percentage']==-99999:
                i['one_year_percentage']='inf'

        return two

    # database logic for categoryview -> top_keywords

    def funcGen(countryname,channel,needstate,category,abs_channel):
        mydb   = myclient[category]
        mycol=mydb[Cname_EugenieTable+countryname]
        ld = mycol.find().sort('Date', -1).limit(1)
        rd = json.loads(dumps(ld, indent=2))

        if rd:
    
            latest_date_str =rd[0]['Date']
            latest_date = datetime.strptime(latest_date_str, '%Y-%m-%d')
            
            three_months=relativedelta(months=int(6))
            three_months_back_date=latest_date-three_months
            three_months_back_date=str(three_months_back_date.isoformat())
            
            latest_date=str(latest_date.isoformat())
            dat = mycol.aggregate([
                {
                    "$match": {
                        'Keyword':None,
                         "Date": { "$gte":  three_months_back_date, "$lt": latest_date }
                    }
                },
                {
                "$group" : {
                    "_id" : "$Need state", 
                    "total_abs": { "$sum" : abs_channel }
                    }
                }])
            data_total = mycol.aggregate( [{
                    "$match": {
                        'Keyword':None,
                         "Date": { "$gte":  three_months_back_date, "$lt": latest_date }
                    }
                },
                {
                "$group" : {
                    "_id" : "", 
                    "total_abs": { "$sum" : abs_channel }
                    }
                     }]
                    )

            dat_res = json.loads(dumps(dat))
            data_total_res = json.loads(dumps(data_total))
           
            if needstate == 'null' or not needstate:
                dat_res=[i for i in dat_res if i['_id']]
            else:
                dat_res=[i for i in dat_res if i['_id']==needstate]
            

            if dat_res:
                res_us= dat_res[0]  
                res_us['chatter_volume']=dat_res[0]["total_abs"]
                res_us['chatter_intensity'] = round(dat_res[0]["total_abs"]*100/data_total_res[0]['total_abs'], 2)
                res_us['region'] = countryname
                del res_us["_id"]
            else:
                res_us = {}


            return res_us

        else:
            return {}

    def trend_regions(request):
        category = request.GET.get('category')
        channel = request.GET.get('channel')
        country = request.GET.get('country')
        needstate = request.GET.get('needstate')

        if channel == "all":
            abs_channel = "$Abs"
            DocCount = "$DocCount"
        else:
            abs_channel = "$Abs"+channel
            DocCount = "$DocCount"+channel

        res = []
        countries = CategoryView.countries(request)
        for i in countries:
            res.append(CategoryView.funcGen(i,channel,needstate,category,abs_channel))
            
        return res

    # database logic for categoryview -> all_needstate
    def all_needstate(request):
        category  = request.GET.get('category')
        country  = request.GET.get('country')
        date_filter = request.GET.get('date')
        sentiment_key = request.GET.get('sentiment_key')

        if sentiment_key == 'null':
            sentimentkey = 'abs'
        elif not sentiment_key:
            sentimentkey = 'abs'
        else:
            sentimentkey = sentiment_key
        

        mydb   = myclient[category]
        mycol  = mydb[Cname_EugenieTable + country]

        abs_channel       = request.GET.get('abs_channel')
        sentiment_channel = request.GET.get('sentiment_channel')

        if abs_channel == 'all':
            abs_channel = ""
        if sentiment_channel  == 'all':
            sentiment_channel = ""

        pos_val = "$PoS_M"+abs_channel.replace("_","",1)
        neg_val = "$Neg_M"+abs_channel.replace("_","",1)
        neut_val= "$Neutral"+abs_channel.replace("_","",1)
        
        abs_channel = "$Abs" + abs_channel
        sentiment_channel = "$Sentiment" + sentiment_channel

        #extract sentiment
        
        if category is None:
            return {"code":400, "msg":"category Required"}

        ld = mycol.find().sort('Date', -1).limit(1)
        rd = json.loads(dumps(ld, indent=2))
    
        latest_date_str =rd[0]['Date']
        latest_date = datetime.strptime(latest_date_str, '%Y-%m-%d')


        three_months=relativedelta(months=int(date_filter))
        three_months_back_date=latest_date-three_months
        three_months_back_date=str(three_months_back_date.isoformat())
        
        latest_date=str(latest_date.isoformat())

        # query needstate data
        total_abs_query = mycol.aggregate([
            {
                "$match": {
                    'Keyword': None,
                    "Date": { "$gte":  three_months_back_date, "$lt": latest_date }
                }
            },
            {
            "$group" : {
                "_id" : "",
                 "total_abs": { "$sum" : abs_channel },
                "total_pos": { "$sum" : pos_val },
                "total_neg": { "$sum" : neg_val },
                "total_nuet": { "$sum" : neut_val }
            }
        }
        ])

        
        total_absm = json.loads(dumps(total_abs_query))[0]['total_'+sentimentkey]
        
        total_abs_query.close()
        

        query = mycol.aggregate([
            {
                "$match": {
                    'Keyword':None,
                     "Date": { "$gte":  three_months_back_date, "$lt": latest_date }
                }
            },
            {
            "$group" : {
                "_id" : "$Need state", 
                "total_abs": { "$sum" : abs_channel },

                 "total_sent": {
                 "$sum" : { 
                    "$multiply" : [abs_channel,sentiment_channel]
                          }
                    },
                "total_pos":{
                    "$sum": pos_val
                    },
                "total_neg":{
                    "$sum": neg_val
                    },
                "total_nuet":{
                    "$sum": neut_val
                    },  
                }
            }])

        data = json.loads(dumps(query))
        query.close()
        


        
        # query keyword data
        
        query_KW = mycol.aggregate([
            {
                "$match": {
                    'Keyword' : {"$ne" : None},
                    "Date": { "$gte":  three_months_back_date, "$lt": latest_date }
                }
            },
            {
            "$group" : {
                 "_id":{
                        "NS":"$Need state",
                        "KW":"$Keyword",
                     },
                "total_abs": { "$sum" : abs_channel },

                 "total_sent": {
                 "$sum" : { 
                    "$multiply" : [abs_channel,sentiment_channel]
                          }
                    },
                "total_pos":{
                    "$sum": pos_val
                    },
                "total_neg":{
                    "$sum": neg_val
                    },
                "total_nuet":{
                    "$sum": neut_val
                    },  
                }
            }])

        data_KW = json.loads(dumps(query_KW))
        query_KW.close()

        for i in data:
            i['total_perc'] = round((i["total_"+sentimentkey] / total_absm) *100,2)

        
        dict = {
                "name": '',
                "children" : []
            }

        res = []
        sent_temp=0

        range_color_map=["#f05c5c","#F5A623","#50e3c2"]
        range_color_val=[-1,-0.05,0.05]

        range_color_val=[-1.1,-0.9,-0.8,-0.7,-0.6,-0.5,-0.4,-0.3,-0.2,-0.1,0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
        range_color_map=["#FF3344","#FF2E2E","#FF3A29","#FF5024","#FF671F","#FF7E1A","#FF9714","#FFB00F","#FFCA0A","#FFE405","#FFFF00","#C1E600","#A4D900","#89CC00","#6FBF00","#57B300","#42A600","#2E9900","#1C8C00","#0D8000"]
               
        
        for i in data:
            dict['name'] = i["_id"]
            dict['collapsed']='true'
            if i["total_abs"]==0:
                sent_temp=0
            else:
                sent_temp=i["total_sent"]/i["total_abs"]
            dict['total_abs']= i["total_"+sentimentkey]
            dict['sent_temp']= sent_temp
            dict['total_perc']=round(100*(i['total_'+sentimentkey]/total_absm),2)
            dict['color']=range_color_map[bisect.bisect_left(range_color_val,sent_temp)-1]

      
            kwlist= [k for k in data_KW if k['_id']['NS']==i["_id"]]

            dict['children']=[
                {
                    'name':j['_id']['KW'],
                    'total_abs':j['total_'+sentimentkey],
                    'color':range_color_map[bisect.bisect_left(range_color_val,
                    float(0 if j["total_abs"]==0 else j["total_sent"]/j["total_abs"])        
            )-1],
            'sentnorm':float(0 if j["total_abs"]==0 else j["total_sent"]/j["total_abs"]) ,
            
            } for j in kwlist]

            res.append(dict.copy())

        maxVal=-1
        maxKW='a'

        minVal=1
        minKW='a'
        for i in res:
            for k in i['children']:
                if k['sentnorm']>maxVal:
                    maxVal=k['sentnorm']
                    maxKW=k['name']
                    maxNS=i['name']
                elif k['sentnorm']<minVal:
                    minVal=k['sentnorm']
                    minKW=k['name']
                    minNS=i['name']
                del k['sentnorm']

        res=sorted(res, key = lambda i: i['total_abs'],reverse=True) 

        for i in res:
            temp=sorted(i['children'], key = lambda i: i['total_abs'],reverse=True) 
            i['children']=temp[0:min(20,len(temp))]
        
        return [res,total_absm,[maxVal,maxKW,maxNS,minVal,minKW,minNS]]
   
    # database logic for categoryview -> associated_keywords
    def associated_keywords(request):
            
        colorsArr = ['#23CAF5','#2E5BFF','#8C54FF','#5cbdb5','#49BEB7','red']
        category = request.GET.get('category')
        country = request.GET.get('country')
        keywordfromtable = request.GET.get('keywordfromtable')
        if keywordfromtable == "null" or not keywordfromtable:
            keywordfromtable = None
        

        mydb   = myclient[category]
        mycol  = mydb["associated_keywords_" + country]
        mycol2= mydb[Cname_EugenieTable + country]

        distinctIdCode = [
            {"$match": {
                    'Keyword' : {"$ne" : None}
        }
            }, 
        {"$group":
        { "_id": { "NScode": "$Need state", "KWcode": "$Keyword" } 
        } 
        }]
        query2=mycol2.aggregate(distinctIdCode)
        resNsdict = json.loads(dumps(query2))
        NS_map_dict={}

        for i in range(len(resNsdict)):
            NS_map_dict.update({resNsdict[i]["_id"]["KWcode"]:resNsdict[i]["_id"]["NScode"]})
    
    
        keyword = request.GET.get('keyword')
        if len(keyword.split(',')) > 1:
            keyword = [i for i in keyword.split(',')]

        needstate = request.GET.get('needstate')
        channel= request.GET.get('channel')
        date= request.GET.get('date')
        
        if channel is not None:
            if channel == 'all':
                channel = None
            elif len(channel.split("_")) > 1:
                channel = channel.split("_")[1]

        if needstate is None:
            return {"code":400, "msg":"needstate Required"}

        ignore = {"_id":0, "Category":0, "Channel": 0, "Date":0, "Market": 0, "NS": 0,"Unnamed: 0":0}
        sortq={"$sort" : { "cooc" : -1 } }
        if keywordfromtable:
            if channel is None:
                group = {
                "$group" : {
                        "_id":{
                            "KW":"$KW",
                            "term1":"$term1",
                            "term2":"$term2"
                        }, "cooc": { "$sum" : "$cooc" },
                    }
                }
                
                if (keyword == "null")|(keyword is None)|(keyword == ''):
                    query=mycol.aggregate([
                    {
                    "$match": {"$or":[{'NS' : needstate,"Date" : int(date)},{'KW' : keywordfromtable,"Date" : int(date)}]}
                    },
                    group,sortq
                    ])
                elif type(keyword) == list:
                    
                    query=mycol.aggregate([
                    {
                        "$match":{"$or":[ {'NS' : needstate,"KW":{"$in": keyword},"Date" : int(date)},{'KW' : keywordfromtable,"Date" : int(date)}]}
                    },
                    group,sortq
                    ])
                else:
                    
                    query=mycol.aggregate([
                    {
                        "$match":{"$or":[{'NS' : needstate,"KW":keyword,"Date" : int(date)},{'KW' : keywordfromtable,"Date" : int(date)}]}
                    },
                    group,sortq
                    ])
                query.batch_size(500000) 
                res = json.loads(dumps(query))
                query.close()
                output=[]
                for i in res:
                    temp=i["_id"]
                    temp["cooc"]=i['cooc']
                    output.append(temp)
                res=output

            else:           
                query = {'$or':[{'NS' : needstate,'Channel': channel, "Date" : int(date)},{'KW' : keywordfromtable,"Date" : int(date),'Channel': channel}]}
                if (keyword == "null")|(keyword is None):
                    pass
                elif type(keyword) == list:
                    query['KW'] = {"$in": keyword}
                else:
                    query['KW'] = keyword
                data = mycol.find(query,ignore)
                data.batch_size(50000) 
                res = json.loads(dumps(data))
                data.close()
        else:
            if channel is None:
                group = {
                "$group" : {
                        "_id":{
                            "KW":"$KW",
                            "term1":"$term1",
                            "term2":"$term2"
                        }, "cooc": { "$sum" : "$cooc" },
                       
                    },

                }
                if (keyword == "null")|(keyword is None)|(keyword == ''):
                    query=mycol.aggregate([
                    {
                    "$match": {'NS' : needstate,"Date" : int(date)}
                    },
                    group,sortq
                    ])
                elif type(keyword) == list:
                    
                    query=mycol.aggregate([
                    {
                        "$match": {'NS' : needstate,"KW":{"$in": keyword},"Date" : int(date)}
                    },
                    group,sortq
                    ])
                else:
                    
                    query=mycol.aggregate([
                    {
                        "$match": {'NS' : needstate,"KW":keyword,"Date" : int(date)}
                    },
                    group,sortq
                    ])
                query.batch_size(500000) 
                res = json.loads(dumps(query))
                query.close()
                output=[]
                for i in res:
                    temp=i["_id"]
                    temp["cooc"]=i['cooc']
                    output.append(temp)
                res=output

            else:           
                query = {'NS' : needstate,'Channel': channel, "Date" : int(date)}
                if (keyword == "null")|(keyword is None):
                    pass
                elif type(keyword) == list:
                    query['KW'] = {"$in": keyword}
                else:
                    query['KW'] = keyword
                data = mycol.find(query,ignore)
                data.batch_size(50000) 
                res = json.loads(dumps(data))
                data.close()

        
        kws = []
        

        api = {
                'Category' : category,
                'NS' : needstate,
                "data" : []
            }

        nodeset = set()
        nkeywordset = set()
        keywordset = []
        # print(res, 'res')
        flag = 0
        kw = ''
        newRes = []
        tempRes = []
        res = [i for i in res if i['cooc']>10]

                    
        for i in res:
            nkeywordset.add(i['KW'])
        if keywordfromtable:
            for i in range(min(5,len(nkeywordset))):
                keywordset.append(nkeywordset.pop())
            keywordset.append(keywordfromtable)
        else:
            for i in range(min(5,len(nkeywordset))):
                keywordset.append(nkeywordset.pop())
        for i in res:
            if i['KW'] in keywordset:
                newRes.append(i)
        # print(newRes, 'newRes')
    
        if newRes:
            maxVal = max(map(itemgetter('cooc'), newRes))
            maxValNode = 0
            for i in newRes:
                
                i['from'] = i['term1']
                i['to'] = i['term2']
                i['value'] = i['cooc']
                i['width']=(i['cooc']*15)/maxVal 
                
                del i['term1']
                del i['term2']
                del i['cooc']
                # del i['KW']
                nodeset.add(i['from'])
                nodeset.add(i['to'])
            
            nodesize1 = Counter(map(itemgetter('from'), newRes))
            nodesize2 = Counter(map(itemgetter('to'), newRes))
            nodesize = nodesize1+nodesize2
            maxValNode = max(list((nodesize).values()))
            # maxValNode = max(i for i in values.nodesize)
            nodesArr = [] 
            # print(keywordset, 'keywordset')
            mapKwToColors = {}
            z = 0
            
            
            legends={}
            zin=0
            legendcolors=["red","green","blue","brown","pink","cyan","orange","purple","#f45905","#c70d3a","#512c62","#45969b","#de6b35","#380e7f","#e3b04b","#007944","#df42d1","#ffd739","#5f6769"]
            nodesetlist=list(nodeset)
            for i in nodesetlist:
                temp_NS=NS_map_dict.get(i,"none")
                if temp_NS!="none":
                    if legends.get(temp_NS,"none")=="none":
                        legends.update({temp_NS:legendcolors[zin]})
                        zin+=1
            
            for kw in keywordset:
                mapKwToColors[kw] = colorsArr[z] 
                z+=1
            k = 0   
            l = 0
            currTempColor = colorsArr[0]
            for i in nodeset:
                
                k=0
                for j in keywordset:
                    
                    if(i == j):
                        k+=1
                        # print(i,j)
                    
                if k>0:
                    if keywordfromtable and keywordfromtable==i:
                        clrbg='#ea3592'
                        fntclr='white'
                    else:
                        clrbg='white'
                        fntclr='black'

                    nodesArr.append({"id":i,"label":i,"shape":"circle",
                    "font":{
                        "color":fntclr,
                        
                    },
                    #"color":mapKwToColors[i]
                    "color":{
                        "background":clrbg,
                        "border":"black"
                    }
                    })
                    currTempColor = colorsArr[l]
                    l+=1
                    
                else:
                    for m in newRes:
                        if i == m['from'] or i == m['to']:
                            cnt = 0
                            for t in newRes:
                                tempKw = ''
                                if(i == t['from'] or i == t['to']):
                                    tempKw = t['KW']
                                    cnt+=1
                            if cnt>1:
                                flag = True
                            else:
                                flag = False
                            
                            if NS_map_dict.get(i,"none")!="none":
                                clr=legends.get(NS_map_dict.get(i,"none"))
                                lbl="<b>"+i+"</b>"
                                fnt={
                        "color":clr,
                        "multi": 'html',
                        "bold":"35px arial"
                    }

                            else:
                                clr="black"
                                lbl=i
                                fnt={
                                    "multi": 'html',
                                    "size":30
                                }

                            if flag:
                                nodesArr.append({"id":i,
                                "label":lbl,
                                "value":nodesize[i]*800/maxValNode,
                                "font":fnt,
                        "shape":"text"
                    
        })
                                break
                            else:
                                if NS_map_dict.get(i,"none")!="none":
                                    clr=legends.get(NS_map_dict.get(i,"none"))
                                    lbl="<b>"+i+"</b>"
                                    fnt={
                        "color":clr,
                        "multi": 'html',
                        "bold":"35px arial"
                    }
                                else:
                                    # clr=mapKwToColors[m['KW']]
                                    clr="black"
                                    lbl=i
                                    fnt={
                                    "multi": 'html',
                                    "size":30
                                }

                                nodesArr.append({"id":i,
                                # "label":"<b>"+i+"</b>",
                                 "label":i,
                                "value":nodesize[i]*800/maxValNode,
                                
                        "shape":"text",
                    "font":{
                        "color":clr,
                        "multi": 'html',
                        "bold":"35px arial"
                    },

        })
                                break
            from brand.models import BrandView
            brands_d = BrandView.brands(request)
            brands_data = []
            for i in brands_d:
                brands_data.append(i["Game"])
            dataRet = [{"nodes":nodesArr, "edges":newRes},{"legends":legends}, {"brands_d": brands_data}]
        else:
            dataRet = []
            
        return dataRet

    # database logic for categoryview -> keyword_split_channel    
    def keyword_split_channel(request):
        category  = request.GET.get('category')
        country = request.GET.get('country')

        mydb   = myclient[category]
        mycol  = mydb[Cname_EugenieTable + country]

        needstate = request.GET.get('needstate')
        keyword = request.GET.get('keyword')

        if needstate is None:
            return {"code":400, "msg":"needstate Required"}

        if keyword == 'null':
            keyword = None
        else:
            keyword = keyword.split(",")
            kws = []
            for i in keyword:
                kws.append(i)
            keyword = kws[-1]

        today       = datetime.today()
        today=str(today.isoformat())
        three_year_back_date=str(datetime(2017,1,1).isoformat())

        if category:
            query    = { 'Need state' : needstate,'Keyword':keyword,
            "Date": { "$gte":  three_year_back_date, "$lt": today }
        }

        api = {
            # 'Keyword' : keyword,
            'Category' : category,
            'NS' : needstate,
            "data" : []
        }

        ignore   = {"_id":0,
        "Date":1,
        "Abs_Consumer opinions":1,
        "Abs_Forum":1,
        "Abs_Twitter":1,
        "Abs_Video and Photo Sharing":1,
        "Abs_Social network":1,
        "Interest":1,
        "freq_rel":1
        }
        query = mycol.find(query, ignore)
        query.batch_size(50000) 
        res = []
        for i in query:
            res.append(i)
        query.close()

    
        for i in res:
            try:
                if i['Abs_Twitter'] == None:
                    i['Abs_Twitter'] = 0
            except KeyError:
                i['Abs_Twitter'] = 0
            if i['Abs_Social network'] == None:
                i['Abs_Social network'] = 0
            if i['Abs_Video and Photo Sharing'] == None:
                i['Abs_Video and Photo Sharing'] = 0
            # if i['freq_rel'] == None:
                # i['freq_rel'] = 0
            if i['Abs_Consumer opinions'] == None:
                i['Abs_Consumer opinions'] = 0
            if i['Abs_Forum'] == None:
                i['Abs_Forum'] = 0
            # if i['Interest'] == None:
                # i['Interest'] = 0
        api['data'] = res
        return api
        
    # database logic for categoryview -> keyword_split_channel    
    def keyword_split_channel(request):
        category  = request.GET.get('category')
        country = request.GET.get('country')

        mydb   = myclient[category]
        mycol  = mydb[Cname_EugenieTable + country]

        needstate = request.GET.get('needstate')
        keyword = request.GET.get('keyword')

        if needstate is None:
            return {"code":400, "msg":"needstate Required"}

        if keyword == 'null':
            keyword = None
        else:
            keyword = keyword.split(",")
            kws = []
            for i in keyword:
                kws.append(i)
            keyword = kws[-1]

        today       = datetime.today()
        today=str(today.isoformat())
        three_year_back_date=str(datetime(2017,1,1).isoformat())

        if category:
            query    = { 'Need state' : needstate,'Keyword':keyword,
            "Date": { "$gte":  three_year_back_date, "$lt": today }
        }

        api = {
            # 'Keyword' : keyword,
            'Category' : category,
            'NS' : needstate,
            "data" : []
        }

        ignore   = {"_id":0,
        "Date":1,
        "Abs_Consumer opinions":1,
        "Abs_Forum":1,
        "Abs_Twitter":1,
        "Abs_Video and Photo Sharing":1,
        "Abs_Social network":1,
        "Interest":1,
        "freq_rel":1
        }
        query = mycol.find(query, ignore)
        query.batch_size(50000) 
        res = []
        for i in query:
            res.append(i)
        query.close()

    
        for i in res:
            try:
                if i['Abs_Twitter'] == None:
                    i['Abs_Twitter'] = 0
            except KeyError:
                i['Abs_Twitter'] = 0
            if i['Abs_Social network'] == None:
                i['Abs_Social network'] = 0
            if i['Abs_Video and Photo Sharing'] == None:
                i['Abs_Video and Photo Sharing'] = 0
            # if i['freq_rel'] == None:
                # i['freq_rel'] = 0
            if i['Abs_Consumer opinions'] == None:
                i['Abs_Consumer opinions'] = 0
            if i['Abs_Forum'] == None:
                i['Abs_Forum'] = 0
            # if i['Interest'] == None:
                # i['Interest'] = 0
        api['data'] = res
        return api

    # database logic for categoryview -> chatter_volume_for_different_channels   
    def chatter_volume_for_different_channels(request):
        category  = request.GET.get('category')
        country = request.GET.get('country')

        mydb   = myclient[category]
        mycol  = mydb[Cname_EugenieTable + country]

        needstate = request.GET.get('needstate')
        keyword = request.GET.get('keyword')

        # if needstate == "fragrance":
        #     needstate = needstate.replace("/", "")

        if needstate is None:
            return {"code":400, "msg":"needstate Required"}

        if keyword == 'null':
            keyword = []
        elif not keyword:
            keyword = []
        else:
            keyword = keyword.split(",")
            # kws = []
            # for i in keyword:
            #     kws.append(i)
            # keyword = kws[-1]

        ld = mycol.find().sort('Date', -1).limit(1)
        rd = json.loads(dumps(ld, indent=2))
        latest_date_str =rd[0]['Date']
        latest_date = datetime.strptime(latest_date_str, '%Y-%m-%d')
        today = latest_date
        three_year_back_date=today-relativedelta(months=6)
        today=str(today.isoformat())

        three_year_back_date=str(three_year_back_date.isoformat())
        if keyword:
            queryFilter    = { 'Need state' : needstate,'Keyword': {"$in": keyword},
            "Date": { "$gte":  three_year_back_date, "$lt": today }
        }
        else:
            queryFilter    = { 'Need state' : needstate,
            "Date": { "$gte":  three_year_back_date, "$lt": today }
        }


        api = {
            'Keyword' : keyword,
            'Category' : category,
            'NS' : needstate,
          }

        ignore   = {"_id":0,
            "Date":1,
            "Abs_Consumer opinions":1,
            "Abs_Forum":1,
            "Abs_Twitter":1,
            "Abs_Video and Photo Sharing":1,
            "Abs_Social network":1,
            "Interest":1,
            "freq_rel":1
        }
        query = mycol.aggregate(
                    [
                        {
                            "$match": queryFilter
                        },
                        {
                        "$group":
                            {
                            "_id":None,
                            "Abs_Video and Photo Sharing": { "$sum": "$Abs_Video and Photo Sharing" }, 
                            "Abs_Forum":{"$sum": "$Abs_Forum"}, 
                            "Abs_Social network":{"$sum": "$Abs_Social network"},
                            "Abs_Consumer opinions":{"$sum": "$Abs_Consumer opinions"},
                            "Abs_Twitter":{"$sum": "$Abs_Twitter"}
                            }
                        }
                    ]
                )



        query.batch_size(50000) 
        res = []
        for i in query:
            del i['_id']
            res.append(i)
        query.close()



        for i in res:
            try:
                if i['Abs_Twitter'] == None:
                    i['Abs_Twitter'] = 0
            except KeyError:
                i['Abs_Twitter'] = 0
            if i['Abs_Social network'] == None:
                i['Abs_Social network'] = 0
            if i['Abs_Video and Photo Sharing'] == None:
                i['Abs_Video and Photo Sharing'] = 0
            if i['Abs_Consumer opinions'] == None:
                i['Abs_Consumer opinions'] = 0
            if i['Abs_Forum'] == None:
                i['Abs_Forum'] = 0
        newres = []

        keys = list(res[0].keys())
        for i in keys:
            newres.append({
                "channel":i.replace("Abs_",""),
                "value":res[0][i]                
            })

        query2 = mycol.find(queryFilter, ignore)
        query2.batch_size(50000) 
        res2 = []
        for i in query2:
            res2.append(i)
        query2.close()

        keyschannel=res2[0].keys()
        keyschannel=[i for i in keyschannel if i!='Date']

        restrend=[]
        for i in res2:
            for j in keyschannel:
                try:
                    if i[j] == None:
                        val=0
                    else:
                        val=i[j]

                except KeyError:
                    val=0
                restrend.append({'value':val,'channel':j.replace("Abs_",""),'Date':i['Date'][0:8]+"01"})
        restrend=sorted(restrend, key = lambda k:k['Date'])


        
        from itertools import groupby
        from operator import itemgetter
        grouper = itemgetter("Date", "channel")
        result = []
        for key, grp in groupby(sorted(restrend, key = grouper), grouper):
            temp_dict = dict(zip(["Date", "channel"], key))
            temp_dict["value"] = sum(item["value"] for item in grp)
            result.append(temp_dict)
        


        grouper = ['Date']
        key = itemgetter(*grouper)
        result.sort(key=key)
        overall_channel= [{**dict(zip(grouper, k)), 'value': sum(map(itemgetter('value'), g)), 'channel':'overall', 'Date': k} for k, g in groupby(result, key=key)]
        for i in overall_channel:result.append(i)

        api['datatrend'] = result
        api['datapie'] = newres


        return api

    # database logic for categoryview -> forecast  
    def forecast(request):
        category  = request.GET.get('category')
        needstate = request.GET.get('needstate')
        channel   = request.GET.get('channel')
        channel   = channel.replace("_","")
        country = request.GET.get('country')
        sov = request.GET.get('sov')

        mydb   = myclient[category]
        mycol = mydb[Cname_ForecastTable + country]
        mycol2  = mydb[Cname_EugenieTable + country]


        abs_key = "Abs"
        sov_key="SoV"
        if channel == "all":
            abs_key = "Abs"
            sent_key= "Sentiment"
            sov_key="SoV"
        else:
            abs_key ="Abs_"+channel
            sent_key ="Sentiment_"+channel
            sov_key="SoV_"+channel

        
        if sov:
            querySent = mycol2.find({'Keyword' : None, "Need state":needstate},{"Date":1,abs_key:1,sent_key:1,sov_key:1,"_id":0})
            querySent.batch_size(50000)
            resSent = json.loads(dumps(querySent))
            querySent.close()
            res = [{"date": i['Date'], "needstate":needstate, "prediction_flag":0,abs_key:i[sov_key],"aValue":i[abs_key]} for i in resSent]
            res=sorted(res, key = lambda k:k['date'])

        else:
            query = mycol.find({"channel": channel},{"_id":0,needstate:1})  
            query.batch_size(50000)
            res = json.loads(dumps(query))
            query.close()
            res = res[0][needstate]

            querySent = mycol2.find({'Keyword' : None, "Need state":needstate},{"Date":1,sent_key:1,"_id":0})
            querySent.batch_size(50000)
            resSent = json.loads(dumps(querySent))
            querySent.close()           


        sent_dict={dct['Date']:dct[sent_key] for dct in resSent}

        for i in res:
            i["x"] = i["date"]
            i["ay"] = i[abs_key]
            if sov:
                i["aValue"] = i[abs_key]
            if i['prediction_flag']==1:
                i['Sentiment']=0
            else:
                i['Sentiment']=float(0 if sent_dict[i["date"]] is None else sent_dict[i["date"]])
             
            del i["date"]
            del i[abs_key]


        range_color_map=[[-1.0,-0.1,"#CC333F"],[-0.1,0.1,"#e8eb40"],[0.1,1,"#a6ed51"]]

        for i in res:           
            i['SentiColor'] = [color_map[2] for color_map in range_color_map 
                                                if color_map[0]<=(i['Sentiment']) and 
                                                   color_map[1]>(i['Sentiment'])][0]


        for i in res:
            if i['prediction_flag'] == 1:
                i["color"] = "red"
                i['SentiColor']="grey"
            else:
                i["opacity"] = 1
                i["color"] = "blue"
            del i['prediction_flag']
            del i['needstate']


        return res
    # database logic for categoryview -> positive_emerging_needstates  
    def positive_emerging_needstates(request):
        category          = request.GET.get('category')
        abs           = request.GET.get('abs')
        channel       = request.GET.get('channel')
        country       = request.GET.get('country')

        mydb   = myclient[category]
        mycol  = mydb[Cname_EugenieTable + country]
        mycol2 = mydb[Cname_NeedstateTable + country]

        if category is None:
            return {"code":400, "msg":"category Required"}
        if country is None:
            return {"code":400, "msg":"country Required"}
        if channel is None:
            return {"code":400, "msg":"channel Required"}

        if abs is None:
            return {"code":400, "msg":"abs Required"}
        else:
            if abs == 'Abs':
                AbsM = "$"+abs
            else:
                AbsM = "$Abs" + abs

        if channel=="all":
            channelEmerg="all"
            channel = "Abs"
            sentiment = "Sentiment"
            sov="SoV"
        else:
            channelEmerg=channel.replace("_","")
            channel = "Abs" + channel
            sentiment = "Sentiment" + channel.replace("Abs","")
            sov= "SoV" + channel.replace("Abs","")

            
        # TO BE DELETED LATER
        # if (category == "Surface_care" and country == "IND"):
        #     if channel == 'Abs':
        #         channelEmerg="Abs"
        #     else:
        #         channelEmerg = "Abs"+channelEmerg

        query = mycol2.find({"channel":channelEmerg})
        query.batch_size(50000)
        data=json.loads(dumps(query))
        query.close()

        emerging_NS_pos=[]
        if data:
            emerging_NS=list(data[0]['emerging_needstates'].keys())
            for i in emerging_NS:
                if data[0]['emerging_needstates'][i][0][2]=="Positive":
                    emerging_NS_pos.append(i)
        


        match    = {'Keyword' : None, "Need state": {"$in": emerging_NS_pos} }
        needs    = {channel:1,sentiment:1,sov:1,"_id":0,"Need state":1,"Date":1,"Category":1}
        api = {
            "category":category,
            "data" : []
        }

        query = mycol.find(match, needs)
        query.batch_size(50000)
        res = []
        for i in query:
            res.append(i)
        query.close()

        for i in res:
            i['Sentiment'] = float(0 if i[sentiment] is None else i[sentiment])
        
        
        range_color_map=[[-1.0,-0.1,"#f05c5c"],[-0.1,0.1,"#F5A623"],[0.1,1,"#50e3c2"]]


    
        for i in res:
            
            i['color'] = [color_map[2] for color_map in range_color_map 
                                                if color_map[0]<=(i['Sentiment']) and 
                                                   color_map[1]>(i['Sentiment'])][0]
    
        api['data'] = res

        for i in api['data']:
            i["title"] = i["Need state"]
            i["date"] = i["Date"]
            if i[channel] is not None:
                i["y"] = float(i[channel])
            if i[sov] is not None:
                i["value"] = float(i[sov])
            i["continent"] = i['Category']
            del i['Category']
            del i["Date"]
            
            del i[sentiment]


        return api
        
    # database logic for categoryview -> negative_emerging_needstates  
    def negative_emerging_needstates(request):
        category          = request.GET.get('category')
        abs           = request.GET.get('abs')
        channel       = request.GET.get('channel')
        country       = request.GET.get('country')

        if category is None:
            return {"code":400, "msg":"category Required"}
        if country is None:
            return {"code":400, "msg":"country Required"}
        if channel is None:
            return {"code":400, "msg":"channel Required"}

        mydb   = myclient[category]
        mycol  = mydb[Cname_EugenieTable + country]
        mycol2 = mydb[Cname_NeedstateTable + country]


        if abs is None:
            return {"code":400, "msg":"abs Required"}
        else:
            if abs == 'Abs':
                AbsM = "$"+abs
            else:
                AbsM = "$Abs" + abs

        if channel=="all":
            channelEmerg="all"
            channel = "Abs"
            sentiment = "Sentiment"
            sov="SoV"
        else:
            channelEmerg=channel.replace("_","")
            channel = "Abs" + channel
            sentiment = "Sentiment" + channel.replace("Abs","")
            sov= "SoV" + channel.replace("Abs","")
            
        # TO BE DELETED LATER
        # if (category == "Surface_care" and country == "IND"):
        #     if channel == 'Abs':
        #         channelEmerg="Abs"
        #     else:
        #         channelEmerg = "Abs"+channelEmerg

        query = mycol2.find({"channel":channelEmerg})
        query.batch_size(50000)
        data=json.loads(dumps(query))
        query.close()

        emerging_NS_neg=[]
        if data:
            emerging_NS=list(data[0]['emerging_needstates'].keys())
            for i in emerging_NS:
                if data[0]['emerging_needstates'][i][0][2]=="Negative":
                    emerging_NS_neg.append(i)
        


        match    = {'Keyword' : None , "Need state": {"$in": emerging_NS_neg}}
        needs    = {channel:1,sentiment:1,sov:1,"_id":0,"Need state":1,"Date":1,"Category":1}
        api = {
            "category":category,
            "data" : []
        }

        query = mycol.find(match, needs)
        query.batch_size(50000)
        res = []
        for i in query:
            res.append(i)
        query.close()

        for i in res:
            i['Sentiment'] = float(0 if i[sentiment] is None else i[sentiment])
        
        
        range_color_map=[[-1.0,-0.1,"#f05c5c"],[-0.1,0.1,"#F5A623"],[0.1,1,"#50e3c2"]]


    
        for i in res:
            
            i['color'] = [color_map[2] for color_map in range_color_map 
                                                if color_map[0]<=(i['Sentiment']) and 
                                                   color_map[1]>(i['Sentiment'])][0]


        api['data'] = res

        for i in api['data']:
            i["title"] = i["Need state"]
            i["date"] = i["Date"]
            if i[channel] is not None:
                i["y"] = float(i[channel])
            if i[sov] is not None:
                i["value"] = float(i[sov])
            i["continent"] = i['Category']
            del i['Category']
            del i["Date"]
            del i[sentiment]


        return 

    def brand_split_chart(request, needstate=None):
        category = request.GET.get('category')
        country = request.GET.get('country')
        brandlist = request.GET.get('brands')
        keyword = request.GET.get('keyword')
        own_brand = request.GET.get("own_brand")
        if keyword == 'null':
            keyword = None
        if keyword:
            keyword = keyword.split(",")
        mydb   = myclient[category]
        mycol  = mydb[Cname_EugenieTable_Brand + country]
        channel   = request.GET.get('channel').replace("_","")
        if needstate:
            needstate = needstate
        else:
            needstate   = request.GET.get('needstate')
        if needstate:
            needstate = needstate.replace("/","")
        if channel=="all":
            abs_channel="$Abs"
            PoS_M="$PoS_M"
            Neutral="$Neutral"
            Neg_M="$Neg_M"
        else:
            abs_channel="$Abs_"+channel
            PoS_M="$PoS_M"+channel
            Neutral="$Neutral"+channel
            Neg_M="$Neg_M"+channel
    
        needs    = {abs_channel:1,"_id":0,"Need state":1,"Date":1,"Category":1,"Brands":1}
        
        colors = []
        ld = mycol.find().sort('Date', -1).limit(1)
        rd = json.loads(dumps(ld, indent=2))
        

        if rd:
            latest_date_str =rd[0]['Date']
            latest_date = datetime.strptime(latest_date_str, '%Y-%m-%d')

            three_months= relativedelta(months=6)
            three_months_back_date=latest_date-three_months
            three_months_back_date=str(three_months_back_date.isoformat())
            latest_date=str(latest_date.isoformat())

            if needstate:
                needstate_match = {
                        "$match": {
                            'Keyword':None,
                            'Need state':needstate,
                            "Date": { "$gte":  three_months_back_date, "$lt": latest_date },
                            "Brands":{"$ne":"No brand"},
                        }
                    }
                if keyword:
                    needstate_match = {
                        "$match": {
                            'Keyword':{"$in" : keyword },
                            'Need state':needstate,
                            "Date": { "$gte":  three_months_back_date, "$lt": latest_date },
                            "Brands":{"$ne":"No brand"},
                        }
                    }
                query = mycol.aggregate([
                    needstate_match,
                    {
                    "$group" : {
                    "_id" : {"Brand":"$Brands"},
                        "total_abs": { "$sum" : abs_channel },
                        "t_P":{"$sum": PoS_M}, 
                        "t_N":{"$sum": Neutral},
                        "t_Neg":{"$sum": Neg_M},
                        }
                    }])
            else:
                keyword_match =  {
                        "$match": {
                            'Keyword':None,
                            "Date": { "$gte":  three_months_back_date, "$lt": latest_date },
                            "Brands":{"$ne":"No brand"},
                        }
                    }
                if keyword:
                    keyword_match =  {
                        "$match": {
                            'Keyword':{"$in" : keyword },
                            "Date": { "$gte":  three_months_back_date, "$lt": latest_date },
                            "Brands":{"$ne":"No brand"},
                        }
                    }
                query = mycol.aggregate([
                   keyword_match,
                    {
                    "$group" : {
                    "_id" : {"Brand":"$Brands"},
                        "total_abs": { "$sum" : abs_channel },
                        "t_P":{"$sum": PoS_M}, 
                        "t_N":{"$sum": Neutral},
                        "t_Neg":{"$sum": Neg_M},
                        }
                    }])

            data = json.loads(dumps(query))
            query.close()
            

            total_overall=sum([i['total_abs'] for i in data])
       
            if brandlist:
                brandlist=list(set([own_brand]+ brandlist.split(",")))
                data=sorted(data, key = lambda k:k['total_abs'],reverse=True)
                for i in data:
                    if i["_id"]['Brand'] not in brandlist:
                        i["_id"]['Brand']="others"
                        if i["_id"]['Brand']==own_brand:
                            i["_id"]['Brand']="['bold #ea3592]"+own_brand+"[/]"


                res=[{'brand':i["_id"]['Brand'],'value':i['total_abs'],
                "perc": float(0 if total_overall==0 else round(i['total_abs']*100/total_overall,2)),
                "t_P":i['t_P'],
                "t_N":i['t_N'],
                "t_Neg":i['t_Neg'],
                "perc_t_P":float(0 if total_overall==0 else round(i['t_P']*100/total_overall,2)),
                "perc_t_N":float(0 if total_overall==0 else round(i['t_N']*100/total_overall,2)),
                "perc_t_Neg":float(0 if total_overall==0 else round(i['t_Neg']*100/total_overall,2)),
                } for i in data if i["_id"]['Brand'] in brandlist]

                total_others=sum([i['total_abs'] for i in data if i["_id"]['Brand']=="others"])
                t_P_others=sum([i['t_P'] for i in data if i["_id"]['Brand']=="others"])
                t_N_others=sum([i['t_N'] for i in data if i["_id"]['Brand']=="others"])
                t_Neg_others=sum([i['t_Neg'] for i in data if i["_id"]['Brand']=="others"])
                res.append({'brand':'others','value':total_others,
                    'perc': float(0 if total_overall==0 else round(total_others*100/total_overall,2)),
                    "t_P":t_P_others,
                    "t_N":t_N_others,
                    "t_Neg":t_Neg_others,

                    })

                

            else:
                data=sorted(data, key = lambda k:k['total_abs'],reverse=True)
                lindex=min(7,len(data))

                owndata=[i for i in data if i["_id"]['Brand']==own_brand]
                for i in owndata:
                    if i["_id"]['Brand']==own_brand:
                            i["_id"]['Brand']="['bold #ea3592]"+own_brand+"[/]"

                

                res=[{'brand':i["_id"]['Brand'],'value':i['total_abs'],
                "perc": float(0 if total_overall==0 else round(i['total_abs']*100/total_overall,2)),
                "t_P":i['t_P'],
                "t_N":i['t_N'],
                "t_Neg":i['t_Neg'],
                "perc_t_P":float(0 if total_overall==0 else round(i['t_P']*100/total_overall,2)),
                "perc_t_N":float(0 if total_overall==0 else round(i['t_N']*100/total_overall,2)),
                "perc_t_Neg":float(0 if total_overall==0 else round(i['t_Neg']*100/total_overall,2)),
                } for i in data[0:lindex]+owndata]
                
                otherdata=[i for i in data[lindex:len(data)] if i["_id"]['Brand']!=own_brand]

                total_others=sum([i['total_abs'] for i in otherdata ])
                t_P_others=sum([i['t_P'] for i in otherdata])
                t_N_others=sum([i['t_N'] for i in otherdata])
                t_Neg_others=sum([i['t_Neg'] for i in otherdata])
                res.append({'brand':'others','value':total_others,
                    'perc': float(0 if total_overall==0 else round(total_others*100/total_overall,2)),
                    "t_P":t_P_others,
                    "t_N":t_N_others,
                    "t_Neg":t_Neg_others,

                    })
                
                
            res = list({v['brand']:v for v in res}.values())
            return res
        else:
            return []    
    # database logic for categoryview -> association table
    def association_table(request):
        category      = request.GET.get('category')
        channel       = request.GET.get('channel').replace("_","")
        country       = request.GET.get('country')
        needstate       = request.GET.get('needstate')
        keyword       = request.GET.get('keyword')
        sentikey       = request.GET.get('sentikey')
        sentiment   = request.GET.get('sentiment')


        #to remove later
        if needstate == "sub":
            needstate = "sub format"

        if needstate == "fragrance/":
            needstate = "fragrance"

        if sentiment is None:
            sentikey_all=["Pos","Neg","Neu"]
        elif sentiment == 'null':
            sentikey_all=["Pos","Neg","Neu"]
        else:
            if sentiment == "neutral":
                sentikey_all=["Neu"]
            elif sentiment == "negative":
                sentikey_all=["Neg"]
            elif sentiment == "positive":
                sentikey_all=["Pos"]
            else:
                sentikey_all=["Pos","Neg","Neu"]

        if channel=="all":
            channel="All"

        if category is None:
            return {"code":400, "msg":"category Required"}
        if country is None:
            return {"code":400, "msg":"country Required"}
        if channel is None:
            return {"code":400, "msg":"channel Required"}

        mydb   = myclient[category]
        mycol  = mydb['association_keywords_count_'+country]
        
        if sentikey:
            sentikey_all=[sentikey]
        
        if "Need_state_A" in json.loads(dumps(mycol.find().limit(1)))[0]:
            nscolA="Need_state_A"
            nscolB="Need_state_B"
        else:
            nscolA="Need state_A"
            nscolB="Need state_B"

        if needstate:
            query = {"site_type": channel, nscolA: needstate,"antecedent_lab":{"$in":sentikey_all},"period_sum":{"$in":[3,2]}}
            need = {"_id": 0, nscolA: 1, nscolB: 1, "consequents": 1, "consequents_count": 1}
        
        if keyword:
            if keyword != 'null':
                query = {"site_type": channel,"antecedent":{"$in" : keyword.split(",")}, nscolA: needstate,"antecedent_lab":{"$in":sentikey_all},"period_sum":{"$in":[3,2]}}
                need = {"_id": 0, nscolA: 1, nscolB: 1, "consequents": 1, "consequents_count": 1}

        res = mycol.find(query,need)
        res = json.loads(dumps(res))

        NS_total_list = {}

        for i in res:
            for j in range(len(i['consequents'])):
                    if i[nscolB][j] is not None:
                        nsname=i[nscolB][j]+"__"+i['consequents'][j]
                        nsval=i['consequents_count'][j]

                        if nsname in NS_total_list.keys(): 
                            NS_total_list[nsname]=NS_total_list[nsname]+nsval
                        else:
                            NS_total_list.update({nsname:nsval})
        
        final_res = []
        for i in NS_total_list:
            key=i.split("__")[0]
            value=i.split("__")[1]
            support=NS_total_list[i]
            final_res.append({"key":key, "value": value,"support":support})

        
        topNS=[];
        ns=[i['key'] for i in final_res]
        ns=set(ns)
        ns=list(ns)

        for n in ns:
            tempn=[i for i in final_res if i['key']==n]
            temp=[j["support"] for j in tempn]
            temp=sum(temp) / len(temp)
            topNS.append({"NS":n,"value":temp})


        # topNS=sorted(topNS, key=lambda x:x['value'],reverse=False)
        
        NSlist=[i['NS'] for i in topNS]
        NSlist=NSlist[:min(7,len(NSlist))]

        # final_res=[i for i in final_res if i['key'] in NSlist]
        final_res=sorted(final_res, key=lambda x:x['support'],reverse=True)
        final_res=final_res[:min(30,len(final_res))]

        if keyword != 'null' and keyword:
            topNS=[i['key'] for i in final_res]
        else:  
            topNS=[i['key'] for i in final_res if i['key']!=needstate]
        topNS=list(set(topNS))
        topNS=topNS[:(min(10,len(topNS)))]
        
        
        final_res=[i for i in final_res if i['key'] in topNS]
        top_comb=final_res[:3]
        

        valrange=[i['support'] for i in final_res]
        minv=min(valrange)
        maxv=max(valrange)
        maxmin=maxv-minv

        range_color_val=[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
        range_color_map=["#D0DA75","#A2D05F","#6FC44D","#3CB73E","#2CA955","#178A76","#127779","#0D5468","#093656","#061E43"]
                    
           
        for i in final_res:
            i['support']=round((i['support']-minv)/maxmin,2)
            i['color']="style='color:"+range_color_map[bisect.bisect_left(range_color_val,i['support'])-1]+"'"
            if i['support']<0.1:
                i['color']="style='color:"+"#D0DA75"+"'"
            if  i['support']>0.66:
                i['support']="H"
            elif i['support']>0.33:
                i['support']="M"
            else:
                i['support']="L"

 
        notinc=[i['key'] for i in top_comb]
        
        # ["<span class='keywords'>{}</span>".format(j)+"<span class='pink'> - </span>"+"<span class='supports' "+c+'>'+"{}</span>".format(str(f))]
        
        k={}
        countl={}
        for ele in final_res:
            i,j,f,c=(ele["key"],ele['value'],ele['support'],ele['color'])
            if not k.get(i):
                k[i]=["<span class='keywords'>{}</span>".format(j)+"<span class='supports' "+c+'>'+"{}</span>".format(str(f))]
            else:
                k[i].append("<span class='keywords'>{}</span>".format(j)+"<span class='supports' "+c+'>'+"{}</span>".format(str(f)))

            if not countl.get(i):
                countl[i]=[f]
            else:
                countl[i].append(f)

        countdictM=[]
        countdictL=[]
        for i in countl:
            if i not in notinc:
                if len(countl[i]) > 5:
                    countl[i]= countl[i][:5] 

                countdictM.append({'ns':i,"val":len([j for j in countl[i] if j=="M"])})
                countdictL.append({'ns':i,"val":len([j for j in countl[i] if j=="L"])})
            

        countdictM=sorted(countdictM, key = lambda i: i['val'],reverse=True) 
        countdictL=sorted(countdictL, key = lambda i: i['val'],reverse=True) 
        finalalsoNS=list(set([countdictM[0]['ns'],countdictL[0]['ns']]))

        
        

        final_res = [{"key":x[0],"value":",".join(x[1]).replace(",","<br/>").split("<br/>")} for x in k.items()]
        
        for i in final_res:
            if len(i["value"]) > 5:
                i["value"] = i["value"][:5]
        for i in final_res:
            i["value"] = "<br/>".join(i["value"])      
        
        stmnt=""



        for i in top_comb:
            i['value']="<span class='keywordStatement'>"+ i['value']+"</span>"
            i["key"]="<span class='keywordStatement'>"+ i["key"]+"</span>"
            
        for i in top_comb[:2]:
            stmnt=stmnt+i['value']+", "
        stmnt=stmnt+" and "+top_comb[2]['value']+"."

        try:
            api={
            'data':final_res,
            'statement':stmnt,
            "high":finalalsoNS[0],
            "low":finalalsoNS[1]
            }
        except IndexError:
            api={
            'data':final_res,
            'statement':stmnt,
            "high":finalalsoNS[0],
            "low":None
            }
    

        return api


class TopCards:
    def total_needstate_in_category(request):
        category      = request.GET.get('category')
        channel       = request.GET.get('channel')
        country       = request.GET.get('country')

        if category is None:
            return {"code":400, "msg":"category Required"}
        if country is None:
            return {"code":400, "msg":"country Required"}

        mydb   = myclient[category]
        mycol  = mydb[Cname_EugenieTable + country]
        count = len(mycol.distinct("Need state"))
        return {"count":count}
    
    def top_mentioned(request):
        category      = request.GET.get('category')
        channel       = request.GET.get('channel')
        country       = request.GET.get('country')

        if category is None:
            return {"code":400, "msg":"category Required"}
        if country is None:
            return {"code":400, "msg":"country Required"}

        if channel == "all":
            channel = "$Abs"
        else:
            channel = "$Abs"+channel

        mydb   = myclient[category]
        mycol  = mydb[Cname_EugenieTable + country]
        query = mycol.aggregate([
            {
                "$group" : {
                        "_id" : channel, "total_abs": { "$sum" : channel }
                    }
            },
            {"$sort" : { "total_abs" : -1 } },
            { "$limit" : 1 }
        ])
        highest_mention = json.loads(dumps(query))[0]["total_abs"]
        return {"top_mention":highest_mention}
    
    def bottom_mentioned(request):
        category      = request.GET.get('category')
        channel       = request.GET.get('channel')
        country       = request.GET.get('country')
        brand       = request.GET.get('brand')
        if brand:
            brand = brand.split(",")

        if category is None:
            return {"code":400, "msg":"category Required"}
        if country is None:
            return {"code":400, "msg":"country Required"}

        if channel == "all":
            channel = "$Abs"
        else:
            channel = "$Abs"+channel

        mydb   = myclient[category]
        if brand:
            mycol = mydb[Cname_EugenieTable_Brand + country]
        else:
            mycol  = mydb[Cname_EugenieTable + country]
            
        if brand:
            query = mycol.aggregate([
                {
                    "$match": {"Brands" :{"$in" : brand}}
                },
                {
                    "$group" : {
                            "_id" : {"nsid": "$Need state"}, "total_abs": { "$sum" : channel }
                        }
                },
                {"$sort" : { "total_abs" : 1 } },
                
            ])
        else:
            query = mycol.aggregate([
                {
                    "$group" : {
                            "_id" : {"nsid": "$Need state"}, "total_abs": { "$sum" : channel }
                        }
                },
                {"$sort" : { "total_abs" : 1 } },
                
            ])
        mentions = json.loads(dumps(query))
        
        return {'bottom_mentions':mentions[0]['_id']['nsid'],'top_mentions':mentions[-1]['_id']['nsid']}
         
    def total_no_of_chatter_in_category(request):
        category  = request.GET.get('category')
        country  = request.GET.get('country')
        channel = request.GET.get('channel').replace("_","")

        mydb   = myclient[category]
        mycol  = mydb["chatter_master_data_" + country]
        if channel=='all':
            count = mycol.find().count()
        else:
            count = mycol.find({'site_type':channel}).count()

        return {"count":count}    
