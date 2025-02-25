import { cn } from '@/lib/utils';
import { ChatContext } from '@/models';
import React from 'react';

interface ContextPanelProps {
    context: ChatContext | undefined;
}

export const ContextPael = ({ context } : ContextPanelProps) => {
    if (!context) return (
        <div className='w-full h-full bg-gray-100 rounded-lg p-4 flex flex-col justify-center items-center'>
            <p>No context available</p>
        </div>
    )
    
    const {
        product_ids,
        review_ids,
        running_summary,
    } = context;
    return (
        <div className='w-full h-full bg-gray-100 rounded-lg p-4 flex flex-col gap-2' >
            <LabeledContent label='Running Summary'> 
                <p className="mt-6 text-gray-900 text-sm leading-snug line-clamp-2">
                    {running_summary}
                </p>
            </LabeledContent>
            <LabeledContent label='Vector Store Entities'> 
                <EntityMetrics productIds={product_ids} reviewIds={review_ids} />
            </LabeledContent>
            <LabeledContent label='Intent'> 
                <IntentMetrics intent={context.metadata?.last_query_intent} />
            </LabeledContent>
            <LabeledContent label='LLM'> 
                <TokenTimeMetrics tokens={context.metadata?.last_response_tokens} time={context.metadata?.elapsed_seconds} />
            </LabeledContent>
        </div>
    )
}

interface TokenTimeMetricsProps {
    tokens: number;
    time: number;
}

const TokenTimeMetrics = ({ tokens, time }: TokenTimeMetricsProps) => (
    <div className='w-full pt-4'>
        <div className='pt-3 flex gap-2 text-s'>
            <div className='w-1/2 bg-gray-100 text-left p-3 rounded-lg'>
                <p>Response Tokens: {tokens}</p>
            </div>
            <div className='w-1/2 bg-gray-100 p-3 rounded-lg'>
                <p>Elapsed: {time.toFixed(2)}s</p>
            </div>
        </div>
    </div>
)

interface IntentMetricsProps {
    intent: string
}

const IntentMetrics = ({ intent }: IntentMetricsProps) => {
    const intents = ['knowledge', 'chat', 'search'];
    return (
        <div className='w-full pt-4 flex gap-1 mt-3'>
            {intents.map((i) => (
                <div key={i} className={cn('w-full p-3 text-sm rounded-lg text-center', {
                    'bg-gray-100': i !== intent,
                    'bg-blue-100': i === intent,
                })}>
                    {i}
                </div>
            ))}
        </div>
    );
}

interface EntityMetricsProps {
    productIds: string[] | undefined;
    reviewIds: string[] | undefined;
}

const EntityMetrics = ({ productIds, reviewIds }: EntityMetricsProps) => 
    (
        <div className='w-full pt-4'>
            <div className='pt-3 flex gap-2 text-s'>
                <div className='w-1/2 bg-gray-100 text-left p-3 rounded-lg'>
                    <p>Products: {productIds?.length}</p>
                </div>
                <div className='w-1/2 bg-gray-100 p-3 rounded-lg'>
                    <p>Reviews: {reviewIds?.length}</p>
                </div>
            </div>
        </div>
    )

interface LabeledContentProps extends React.ComponentPropsWithoutRef<'div'> {
    label: string;
    children: React.ReactNode;
}

const LabeledContent = ({ label, children, className }: LabeledContentProps) => (
    <div className={`relative px-3 pt-3 pb-2 border rounded-lg bg-white shadow-md ${className}`}>
        <span className="absolute top-2 left-3 bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded-lg">
        {label}
        </span>
        {children}
    </div>
)