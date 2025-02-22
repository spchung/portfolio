'use client';
import { useContext } from '@/hooks/use-context';
import { Review } from '@/models';
import { EntityPanel} from './entity-panel';


export default function DevPanel() {
  const { context } = useContext();

  const history = context?.history;
  const runningSummary = context?.running_summary;
  const last_prompt = context?.last_prompt;
  const intent = context?.metadata.last_query_intent;
  const product_ids = context?.product_ids;
  const review_ids = context?.review_ids;

  return (
    <div className='flex flex-col h-full'>
      <div className='flex-1'>
        <EntityPanel productIds={product_ids} reviewIds={review_ids} />
      </div>
      <div className='flex-1'> 
        <h2>Summary</h2>
        <p>{runningSummary}</p>
        <h2>Intent: {intent}</h2>
      </div>
    </div>
  )
}