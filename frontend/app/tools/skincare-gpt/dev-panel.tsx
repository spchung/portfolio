'use client';
import { useContext } from '@/hooks/use-context';
import { EntityPanel} from './entity-panel';
import { ContextPael } from './context-panel';

export default function DevPanel() {
  const { context } = useContext();

  const product_ids = context?.product_ids;
  const review_ids = context?.review_ids;


  return (
    <div className='flex flex-col h-full gap-2'>
      <div className='flex-1'>
        <EntityPanel productIds={product_ids} reviewIds={review_ids} />
      </div>
      <div className='flex-1 overflow-y-auto'> 
        <ContextPael context={context} />
      </div>
    </div>
  )
}