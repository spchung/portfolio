V2 will experiment with Qdrant vector store and will also experiment with Multitenancy. 

Multitenancy means storing all vectors into one collection to and use metadata ("payload" in Qdrant terms) to perform filtering and indexing. 

MANDATORY PAYLOAD ATTRS
For this application we will first experiment with using just one index - "entity\_type"
entity\_type will either be 'product' or 'review'. 

For filtering, we will also implement another payload attribute - "vector\_column"
vector\_column will identify what column this vector represents
vector\_column:
\- product\_name
\- product\_ingredients
\- product\_highlights
\- review\_text

universal payload attrs - "product\_id" & 'price'
all points in the Qdrant db will carry this attr in its payload. 

ENTITY SPECIFIC PAYLOAD ATTRS
For Points where 'entity\_type' == 'review'
\- rating
\- is\_recommended
\- review\_title
\- skin\_tone
\- eye\_color
\- skin\_type
\- hair\_color
\- product\_name
\- brand\_name

For Points where 'entity\_type' == 'product'
\- size
\- primary\_category
\- secondary\_category
\- tertiary\_category
\- rating
\- reviews
\- brand\_name

<br>
<br>
<br>
