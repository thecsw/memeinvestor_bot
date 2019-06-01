package utils

func GetDB() (conn string) {
	conn = "user=test password='1234' dbname=db host=postgres port=5432 sslmode=disable"
	return
}
