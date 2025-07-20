CREATE OR REPLACE FUNCTION get_user_by_phone(input_phone text)
RETURNS TABLE (
    id uuid,
    raw_user_meta_data jsonb
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.id,
        u.raw_user_meta_data
    FROM auth.users u
    WHERE 
        u.raw_user_meta_data->>'phone_number' = input_phone;
END;
$$; 