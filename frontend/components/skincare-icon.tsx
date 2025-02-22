import Image from "next/image";

interface IconProps extends React.ComponentPropsWithoutRef<'svg'> {
    type: string;
    className?: string;
    width?: number;
    height?: number;
}

const SkinCareIcon = ({ type, width=30, height=30 } : IconProps) => {

    var source;
    switch (type) {
        case 'Moisturizers':
            source = '/icons/cream.png';
            break;
        case 'Sunscreen':
            source = '/icon/sunscreen.png';
            break;
        case 'Treatments':
            source = '/icons/treatment.png';
            break;
        default:
            source = '/icons/cleanser.png';
            break; 
    }

    return <Image
        src={source}
        alt="Product Image"
        width={width}
        height={height}
    />
}

export { SkinCareIcon };